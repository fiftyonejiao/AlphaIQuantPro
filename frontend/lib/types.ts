export type StrategyType = "indicator" | "script";

export interface Strategy {
  strategy_id: string;
  name: string;
  description: string;
  strategy_type: StrategyType;
  code: string;
  parameters: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Metrics {
  total_return: number;
  cagr: number | null;
  max_drawdown: number;
  sharpe: number | null;
  win_rate: number;
  profit_factor: number | null;
  trade_count: number;
  avg_win: number;
  avg_loss: number;
  exposure_time: number;
  turnover: number;
}

export interface Trade {
  timestamp: string;
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  price: number;
  fee: number;
  reason: string;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
}

export interface BacktestResult {
  backtest_id: string;
  strategy_id: string;
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_equity: number;
  metrics: Metrics;
  equity_curve: EquityPoint[];
  trades: Trade[];
  logs: string[];
  data_source: string;
  is_mock_data: boolean;
  status: string;
  created_at: string;
}

export interface BacktestSummary {
  backtest_id: string;
  strategy_id: string;
  strategy_name: string;
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  status: string;
  total_return: number;
  max_drawdown: number;
  trade_count: number;
  is_mock_data: boolean;
  created_at: string;
}

export type PaperRunStatus = "created" | "running" | "stopped" | "failed" | "completed";

export interface PaperRunState {
  run_id: string;
  strategy_id: string;
  status: PaperRunStatus;
  mode: string;
  symbol: string;
  timeframe: string;
  started_at: string | null;
  stopped_at: string | null;
  initial_capital: number;
  current_equity: number;
  realized_pnl: number;
  unrealized_pnl: number;
  open_positions: { symbol: string; quantity: number; avg_price: number; unrealized_pnl: number }[];
  signals: { timestamp: string; signal: number; price: number; note: string }[];
  orders: { order_id: string; timestamp: string; symbol: string; side: string; quantity: number; status: string }[];
  fills: { order_id: string; timestamp: string; symbol: string; side: string; quantity: number; price: number; fee: number }[];
  trades: Trade[];
  equity_curve: { timestamp: string; equity: number }[];
  metrics: Partial<Metrics>;
  logs: string[];
  data_source: string;
  is_mock_data: boolean;
  post_run_analysis: string;
}

export interface MarketDataStatus {
  qveris_configured: boolean;
  qveris_reachable: boolean;
  active_source: "qveris" | "mock";
  session_id: string;
  notes: string[];
}

export interface MarketDataset {
  meta: {
    provider: string;
    source: string;
    symbol: string;
    timeframe: string;
    currency: string;
    retrieval_timestamp: string;
    quality_notes: string[];
    is_mock: boolean;
  };
  bars: { timestamp: string; open: number; high: number; low: number; close: number; volume: number }[];
}

export interface AppSettings {
  values: Record<string, unknown>;
  deepseek: { provider: string; configured: boolean; model: string; base_url: string };
  qveris: { configured: boolean; reachable: boolean; session_id: string; message: string };
}
