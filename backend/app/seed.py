"""Seed example strategies so the workbench is demoable immediately."""
from sqlalchemy.orm import Session

from .storage.models import StrategyModel

MA_CROSSOVER_CODE = '''\
def generate_signals(df, params):
    """Moving average crossover (long when fast MA > slow MA)."""
    fast = int(params.get("fast_period", 10))
    slow = int(params.get("slow_period", 30))
    fast_ma = df["close"].rolling(fast).mean()
    slow_ma = df["close"].rolling(slow).mean()
    signals = (fast_ma > slow_ma).astype(int)
    return signals.fillna(0)
'''

RSI_REVERSION_CODE = '''\
def generate_signals(df, params):
    """RSI mean reversion: buy oversold, exit when RSI normalizes."""
    period = int(params.get("rsi_period", 14))
    oversold = float(params.get("oversold", 30))
    exit_level = float(params.get("exit_level", 55))

    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-9)
    rsi = 100 - (100 / (1 + rs))

    signals = []
    holding = 0
    for value in rsi.fillna(50):
        if holding == 0 and value < oversold:
            holding = 1
        elif holding == 1 and value > exit_level:
            holding = 0
        signals.append(holding)
    return pd.Series(signals, index=df.index)
'''

BREAKOUT_SCRIPT_CODE = '''\
class Strategy:
    """Event-driven breakout: go long on a new N-bar high, exit on N-bar low."""

    def on_start(self, ctx):
        ctx.state["highs"] = []
        ctx.state["lows"] = []
        ctx.state["lookback"] = int(ctx.params.get("lookback", 20))

    def on_bar(self, ctx, bar):
        highs = ctx.state["highs"]
        lows = ctx.state["lows"]
        lookback = ctx.state["lookback"]
        signal = ctx.position
        if len(highs) >= lookback:
            if bar["close"] > max(highs[-lookback:]):
                signal = 1
            elif bar["close"] < min(lows[-lookback:]):
                signal = 0
        highs.append(bar["high"])
        lows.append(bar["low"])
        return signal
'''

SEED_STRATEGIES = [
    {
        "name": "Moving Average Crossover",
        "description": "Classic trend-following: long when the fast MA is above the slow MA.",
        "strategy_type": "indicator",
        "code": MA_CROSSOVER_CODE,
        "parameters": {"fast_period": 10, "slow_period": 30},
    },
    {
        "name": "RSI Mean Reversion",
        "description": "Buys oversold conditions (RSI < 30) and exits when RSI recovers.",
        "strategy_type": "indicator",
        "code": RSI_REVERSION_CODE,
        "parameters": {"rsi_period": 14, "oversold": 30, "exit_level": 55},
    },
    {
        "name": "Channel Breakout (Script)",
        "description": "Event-driven script strategy: breakout entries on N-bar highs.",
        "strategy_type": "script",
        "code": BREAKOUT_SCRIPT_CODE,
        "parameters": {"lookback": 20},
    },
]


def seed_examples(db: Session) -> None:
    if db.query(StrategyModel).count() > 0:
        return
    for item in SEED_STRATEGIES:
        db.add(StrategyModel(**item))
    db.commit()
