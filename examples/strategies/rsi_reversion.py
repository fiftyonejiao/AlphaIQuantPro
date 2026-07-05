"""Example indicator strategy: RSI mean reversion.

Buys oversold conditions (RSI below `oversold`) and exits when RSI recovers
above `exit_level`.

Parameters: {"rsi_period": 14, "oversold": 30, "exit_level": 55}
"""


def generate_signals(df, params):
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
