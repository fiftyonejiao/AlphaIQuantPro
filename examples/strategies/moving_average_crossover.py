"""Example indicator strategy: moving average crossover.

Paste this into the AlphaQuantPro strategy editor (type: indicator), or POST
it to /api/strategies. Long when the fast MA is above the slow MA, flat
otherwise.

Parameters: {"fast_period": 10, "slow_period": 30}
"""


def generate_signals(df, params):
    fast = int(params.get("fast_period", 10))
    slow = int(params.get("slow_period", 30))
    fast_ma = df["close"].rolling(fast).mean()
    slow_ma = df["close"].rolling(slow).mean()
    return (fast_ma > slow_ma).astype(int).fillna(0)
