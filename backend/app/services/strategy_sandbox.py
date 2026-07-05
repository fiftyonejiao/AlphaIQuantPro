"""Restricted local execution of user strategy code.

WARNING: this is a best-effort restricted namespace for a local-first,
single-user MVP — it is NOT a hardened security sandbox. Strategies run in
the same process with a curated set of builtins and only pandas/numpy/math
available as imports. Do not run untrusted third-party strategy code.
"""
import math
from typing import Any, Callable

import numpy as np
import pandas as pd

_SAFE_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "range": range, "round": round,
    "set": set, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
    "zip": zip, "print": print, "isinstance": isinstance, "Exception": Exception,
    "ValueError": ValueError, "TypeError": TypeError,
    "__build_class__": __build_class__, "__name__": "strategy_sandbox",
}

_ALLOWED_MODULES = {"math": math, "numpy": np, "np": np, "pandas": pd, "pd": pd}


def _restricted_import(name: str, *args: Any, **kwargs: Any):
    if name in _ALLOWED_MODULES:
        return _ALLOWED_MODULES[name]
    raise ImportError(f"import of '{name}' is not allowed in the strategy sandbox")


class StrategySandboxError(RuntimeError):
    pass


def _exec_code(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "__builtins__": {**_SAFE_BUILTINS, "__import__": _restricted_import},
        "pd": pd,
        "np": np,
        "math": math,
    }
    try:
        exec(compile(code, "<strategy>", "exec"), namespace)  # noqa: S102
    except Exception as exc:
        raise StrategySandboxError(f"strategy code failed to load: {exc}") from exc
    return namespace


def load_indicator_strategy(code: str) -> Callable[[pd.DataFrame, dict], pd.Series]:
    """Indicator strategies expose `generate_signals(df, params) -> Series`.

    The returned Series holds target positions per bar: 1 (long) or 0 (flat).
    """
    namespace = _exec_code(code)
    fn = namespace.get("generate_signals")
    if not callable(fn):
        raise StrategySandboxError(
            "indicator strategy must define generate_signals(df, params)"
        )
    return fn


def load_script_strategy(code: str) -> Any:
    """Script strategies expose a `Strategy` class with event hooks.

    Supported hooks: on_start(ctx), on_bar(ctx, bar), on_signal(ctx, signal),
    on_order_update(ctx, order), on_stop(ctx). `on_bar` may return a target
    position (1 long / 0 flat) or call ctx.buy()/ctx.sell().
    """
    namespace = _exec_code(code)
    cls = namespace.get("Strategy")
    if cls is None or not isinstance(cls, type):
        raise StrategySandboxError("script strategy must define a Strategy class")
    try:
        return cls()
    except Exception as exc:
        raise StrategySandboxError(f"failed to instantiate Strategy: {exc}") from exc


def run_indicator_signals(
    code: str, df: pd.DataFrame, params: dict[str, Any]
) -> list[int]:
    fn = load_indicator_strategy(code)
    try:
        result = fn(df.copy(), dict(params))
    except Exception as exc:
        raise StrategySandboxError(f"generate_signals raised: {exc}") from exc
    if isinstance(result, pd.Series):
        values = result.fillna(0).astype(int).tolist()
    elif isinstance(result, (list, tuple, np.ndarray)):
        values = [int(0 if (v is None or (isinstance(v, float) and math.isnan(v))) else v) for v in result]
    else:
        raise StrategySandboxError("generate_signals must return a Series or list")
    if len(values) != len(df):
        raise StrategySandboxError(
            f"signal length {len(values)} != bar count {len(df)}"
        )
    return [1 if v > 0 else 0 for v in values]
