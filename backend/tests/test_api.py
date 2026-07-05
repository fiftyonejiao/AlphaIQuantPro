import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


MA_CODE = """
def generate_signals(df, params):
    fast = df["close"].rolling(int(params.get("fast_period", 5))).mean()
    slow = df["close"].rolling(int(params.get("slow_period", 20))).mean()
    return (fast > slow).astype(int).fillna(0)
"""


class TestStrategiesAPI:
    def test_seeded_examples_exist(self, client):
        resp = client.get("/api/strategies")
        assert resp.status_code == 200
        assert len(resp.json()) >= 3

    def test_crud_lifecycle(self, client):
        created = client.post(
            "/api/strategies",
            json={
                "name": "Test MA",
                "description": "test",
                "strategy_type": "indicator",
                "code": MA_CODE,
                "parameters": {"fast_period": 5, "slow_period": 20},
            },
        )
        assert created.status_code == 201
        sid = created.json()["strategy_id"]

        got = client.get(f"/api/strategies/{sid}")
        assert got.status_code == 200
        assert got.json()["name"] == "Test MA"

        updated = client.put(f"/api/strategies/{sid}", json={"name": "Renamed"})
        assert updated.status_code == 200
        assert updated.json()["name"] == "Renamed"

        deleted = client.delete(f"/api/strategies/{sid}")
        assert deleted.status_code == 204
        assert client.get(f"/api/strategies/{sid}").status_code == 404


class TestBacktestsAPI:
    def _create_strategy(self, client) -> str:
        resp = client.post(
            "/api/strategies",
            json={
                "name": "BT strategy",
                "strategy_type": "indicator",
                "code": MA_CODE,
                "parameters": {},
            },
        )
        return resp.json()["strategy_id"]

    def test_run_backtest_and_fetch_details(self, client):
        sid = self._create_strategy(client)
        resp = client.post(
            "/api/backtests",
            json={
                "strategy_id": sid,
                "symbol": "AAPL",
                "timeframe": "1d",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 100000,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["is_mock_data"] is True
        assert body["metrics"]["trade_count"] > 0
        bid = body["backtest_id"]

        assert client.get(f"/api/backtests/{bid}").status_code == 200
        assert client.get(f"/api/backtests/{bid}/metrics").json()["metrics"]
        assert client.get(f"/api/backtests/{bid}/trades").json()["trades"]
        assert client.get(f"/api/backtests/{bid}/events").json()["logs"]
        assert any(b["backtest_id"] == bid for b in client.get("/api/backtests").json())

    def test_unknown_strategy_404(self, client):
        resp = client.post(
            "/api/backtests",
            json={
                "strategy_id": "nope",
                "start_date": "2023-01-01",
                "end_date": "2023-06-01",
            },
        )
        assert resp.status_code == 404

    def test_invalid_date_range_422(self, client):
        sid = self._create_strategy(client)
        resp = client.post(
            "/api/backtests",
            json={
                "strategy_id": sid,
                "start_date": "2023-06-01",
                "end_date": "2023-01-01",
            },
        )
        assert resp.status_code == 422


class TestPaperRunsAPI:
    def test_full_paper_run_lifecycle(self, client):
        sid = client.post(
            "/api/strategies",
            json={"name": "PR strategy", "strategy_type": "indicator", "code": MA_CODE},
        ).json()["strategy_id"]

        started = client.post(
            "/api/paper-runs",
            json={
                "strategy_id": sid,
                "symbol": "AAPL",
                "mode": "historical_replay",
                "lookback_days": 60,
                "replay_delay_seconds": 0.01,
            },
        )
        assert started.status_code == 201
        run_id = started.json()["run_id"]
        assert started.json()["status"] in ("created", "running")

        time.sleep(0.5)
        state = client.get(f"/api/paper-runs/{run_id}").json()
        assert state["status"] in ("running", "completed", "stopped")
        assert state["is_mock_data"] is True

        stopped = client.post(f"/api/paper-runs/{run_id}/stop")
        assert stopped.status_code == 200
        assert stopped.json()["status"] in ("stopped", "completed")

        events = client.get(f"/api/paper-runs/{run_id}/events").json()
        assert any("SIMULATION ONLY" in log for log in events["logs"])

        analysis = client.get(f"/api/paper-runs/{run_id}/analysis").json()
        assert "deterministic_summary" in analysis
        assert analysis["ai_is_mock"] is True  # no DeepSeek key in tests
        assert "disclaimer" in analysis

    def test_future_exchange_mode_disabled(self, client):
        sid = client.post(
            "/api/strategies",
            json={"name": "X", "strategy_type": "indicator", "code": MA_CODE},
        ).json()["strategy_id"]
        resp = client.post(
            "/api/paper-runs",
            json={"strategy_id": sid, "mode": "exchange_paper_future"},
        )
        assert resp.status_code == 400
        assert "future work" in resp.json()["detail"]


class TestMarketDataAPI:
    def test_status_shows_mock_source(self, client):
        resp = client.get("/api/market-data/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["qveris_configured"] is False
        assert body["active_source"] == "mock"

    def test_fetch_returns_labeled_mock_data(self, client):
        resp = client.post(
            "/api/market-data/fetch",
            json={"symbol": "MSFT", "timeframe": "1d", "start_date": "2024-01-01", "end_date": "2024-02-01"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["is_mock"] is True
        assert len(body["bars"]) > 10

    def test_qveris_status_has_no_secret(self, client):
        resp = client.get("/api/market-data/qveris/status")
        assert resp.status_code == 200
        assert "api_key" not in resp.json()


class TestAnalysisAndSettingsAPI:
    def test_strategy_review_mock_without_key(self, client):
        sid = client.post(
            "/api/strategies",
            json={"name": "Review me", "strategy_type": "indicator", "code": MA_CODE},
        ).json()["strategy_id"]
        resp = client.post(
            "/api/analysis/strategy-review",
            json={"strategy_id": sid, "language": "en"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_mock"] is True
        assert body["provider"] == "deepseek"

    def test_settings_never_expose_keys_and_gate_live_trading(self, client):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        body = resp.json()
        assert body["values"]["live_trading_enabled"] is False
        # Responses may mention env-var *names* (e.g. "QVERIS_API_KEY missing")
        # but must never contain key *values* or api_key fields.
        assert "api_key" not in body.get("deepseek", {})
        assert "api_key" not in body.get("qveris", {})

        # live_trading_enabled cannot be switched on via API
        updated = client.put("/api/settings", json={"values": {"live_trading_enabled": True, "language": "zh-CN"}})
        assert updated.json()["values"]["live_trading_enabled"] is False
        assert updated.json()["values"]["language"] == "zh-CN"
