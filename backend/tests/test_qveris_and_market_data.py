import pytest

from app.schemas.market_data import MarketDataset
from app.services.data_normalization_service import DataValidationError, normalize_ohlcv
from app.services.market_data_service import (
    MarketDataService,
    _build_params,
    _map_qveris_rows,
    generate_mock_ohlcv,
)
from app.services.qveris_client import QverisClient, QverisNotConfiguredError


class TestQverisClient:
    def test_initialization_from_env(self):
        client = QverisClient()
        assert client.base_url.startswith("http")
        assert client.session_id == "alphaquantpro-local"

    def test_missing_api_key_is_not_configured(self):
        client = QverisClient(api_key="")
        assert client.is_configured is False

    def test_placeholder_key_is_not_configured(self):
        client = QverisClient(api_key="your_qveris_api_key_here")
        assert client.is_configured is False

    def test_missing_key_raises_on_real_calls(self):
        client = QverisClient(api_key="")
        with pytest.raises(QverisNotConfiguredError):
            client.discover("stock price")
        with pytest.raises(QverisNotConfiguredError):
            client.inspect(["some.tool"])
        with pytest.raises(QverisNotConfiguredError):
            client.call("some.tool", {})

    def test_status_reports_mock_fallback_when_unconfigured(self):
        status = QverisClient(api_key="").status()
        assert status.configured is False
        assert "mock" in status.message.lower()


class TestMockFallback:
    def test_ohlcv_falls_back_to_mock_without_key(self):
        service = MarketDataService(client=QverisClient(api_key=""))
        dataset = service.get_ohlcv("AAPL", "1d", "2024-01-01", "2024-03-01")
        assert isinstance(dataset, MarketDataset)
        assert dataset.meta.is_mock is True
        assert dataset.meta.source == "mock"
        assert any("MOCK DATA" in n for n in dataset.meta.quality_notes)
        assert len(dataset.bars) > 20

    def test_mock_data_is_deterministic(self):
        a = generate_mock_ohlcv("AAPL", "1d", "2024-01-01", "2024-02-01")
        b = generate_mock_ohlcv("AAPL", "1d", "2024-01-01", "2024-02-01")
        assert a == b

    def test_mock_data_differs_by_symbol(self):
        a = generate_mock_ohlcv("AAPL", "1d", "2024-01-01", "2024-02-01")
        b = generate_mock_ohlcv("MSFT", "1d", "2024-01-01", "2024-02-01")
        assert a != b


class TestQverisResponseMapping:
    """Map real-provider payload shapes (Tiingo / FMP / EODHD) to OHLCV rows."""

    def test_maps_fmp_style_list(self):
        data = [
            {"symbol": "AAPL", "date": "2024-01-12", "open": 186.06, "high": 186.74, "low": 185.19, "close": 185.92, "volume": 40477800},
            {"symbol": "AAPL", "date": "2024-01-11", "open": 186.54, "high": 187.05, "low": 183.62, "close": 185.59, "volume": 49128408},
        ]
        rows = _map_qveris_rows(data)
        assert len(rows) == 2
        bars = normalize_ohlcv(rows)
        assert bars[0].timestamp < bars[1].timestamp
        assert bars[1].close == 185.92

    def test_maps_tiingo_style_adjusted_fields(self):
        data = [{"date": "2024-01-10T00:00:00+00:00", "adjOpen": 100.0, "adjHigh": 102.0, "adjLow": 99.0, "adjClose": 101.0, "adjVolume": 12345}]
        rows = _map_qveris_rows(data)
        assert rows[0]["open"] == 100.0 and rows[0]["close"] == 101.0

    def test_unwraps_dict_wrapped_series(self):
        data = {"results": [{"t": "2024-01-10", "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 10}]}
        rows = _map_qveris_rows(data)
        assert len(rows) == 1 and rows[0]["high"] == 2.0

    def test_skips_rows_missing_ohlc(self):
        data = [{"date": "2024-01-10", "open": 1.0}]  # missing high/low/close
        assert _map_qveris_rows(data) == []


class TestParamBuilding:
    def test_maps_symbol_and_date_range_aliases(self):
        p = _build_params(["ticker", "startDate", "endDate"], "AAPL", "2024-01-01", "2024-02-01", "1d")
        assert p == {"ticker": "AAPL", "startDate": "2024-01-01", "endDate": "2024-02-01"}

    def test_fmp_from_to_aliases(self):
        p = _build_params(["symbol", "from", "to"], "MSFT", "2024-01-01", "2024-02-01", "1d")
        assert p["symbol"] == "MSFT" and p["from"] == "2024-01-01" and p["to"] == "2024-02-01"

    def test_interval_only_for_intraday(self):
        daily = _build_params(["symbol", "interval"], "AAPL", "2024-01-01", "2024-02-01", "1d")
        assert "interval" not in daily
        intraday = _build_params(["symbol", "interval"], "AAPL", "2024-01-01", "2024-02-01", "15m")
        assert intraday["interval"] == "15m"

    def test_falls_back_to_symbol_when_no_known_key(self):
        p = _build_params([], "AAPL", "2024-01-01", "2024-02-01", "1d")
        assert p["symbol"] == "AAPL"


class TestNormalization:
    def _valid_row(self, **overrides):
        row = {
            "timestamp": "2024-01-02T00:00:00+00:00",
            "open": 100.0,
            "high": 105.0,
            "low": 99.0,
            "close": 104.0,
            "volume": 1000.0,
        }
        row.update(overrides)
        return row

    def test_normalizes_valid_bars(self):
        bars = normalize_ohlcv([self._valid_row()])
        assert bars[0].close == 104.0

    def test_epoch_timestamps_are_normalized(self):
        bars = normalize_ohlcv([self._valid_row(timestamp=1704153600)])
        assert bars[0].timestamp.startswith("2024-01-02")

    def test_rejects_empty_payload(self):
        with pytest.raises(DataValidationError):
            normalize_ohlcv([])

    def test_rejects_missing_fields(self):
        row = self._valid_row()
        del row["close"]
        with pytest.raises(DataValidationError, match="missing fields"):
            normalize_ohlcv([row])

    def test_rejects_non_numeric(self):
        with pytest.raises(DataValidationError, match="non-numeric"):
            normalize_ohlcv([self._valid_row(open="not-a-number")])

    def test_rejects_non_positive_price(self):
        with pytest.raises(DataValidationError, match="non-positive"):
            normalize_ohlcv([self._valid_row(low=0)])

    def test_rejects_inconsistent_high_low(self):
        with pytest.raises(DataValidationError, match="inconsistent"):
            normalize_ohlcv([self._valid_row(high=90.0)])

    def test_sorts_and_dedupes(self):
        rows = [
            self._valid_row(timestamp="2024-01-03T00:00:00+00:00"),
            self._valid_row(timestamp="2024-01-02T00:00:00+00:00"),
            self._valid_row(timestamp="2024-01-02T00:00:00+00:00"),
        ]
        bars = normalize_ohlcv(rows)
        assert len(bars) == 2
        assert bars[0].timestamp < bars[1].timestamp
