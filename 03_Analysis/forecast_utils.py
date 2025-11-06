# 03_Python/forecast_utils.py
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX


def load_monthly_revenue(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # normalize columns
    cols_map = {c: c.strip().lower().replace(" ", "") for c in df.columns}
    inv_map = {v: k for k, v in cols_map.items()}

    ym_col = inv_map.get("yearmonth") or inv_map.get("month")
    if ym_col is None:
        raise ValueError("monthly_revenue.csv must contain 'YearMonth' column.")

    amt_col = None
    for k, v in cols_map.items():
        if "lineamount" in v or v == "revenue":
            amt_col = k
            break
    if amt_col is None:
        raise ValueError("monthly_revenue.csv must contain 'LineAmount' (or 'Revenue').")

    out = df[[ym_col, amt_col]].copy()
    out.columns = ["YearMonth", "LineAmount"]
    out["ds"] = pd.to_datetime(out["YearMonth"].astype(str) + "-01") + pd.offsets.MonthEnd(0)
    out = out.sort_values("ds").reset_index(drop=True)
    return out


def fit_sarimax(y: pd.Series, seasonal_periods: int = 12):
    """
    Simple heuristic SARIMAX:
    - ARIMA(1,1,1) with seasonal (1,1,1, m=12) if enough data
    - Falls back to non-seasonal if series is short
    """
    y = pd.Series(y).astype(float)
    if len(y) < seasonal_periods + 6:
        # too short for seasonal; use non-seasonal ARIMA(1,1,1)
        order = (1, 1, 1)
        seasonal_order = (0, 0, 0, 0)
    else:
        order = (1, 1, 1)
        seasonal_order = (1, 1, 1, seasonal_periods)

    model = SARIMAX(
        y,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    return model


def forecast_sarimax(model, periods: int = 12):
    fc_res = model.get_forecast(steps=periods)
    mean = fc_res.predicted_mean
    conf = fc_res.conf_int(alpha=0.2)  # ~80% band
    return mean, conf


def build_forecast_frame(last_ds: pd.Timestamp, yhat: pd.Series, conf: pd.DataFrame):
    future_idx = pd.date_range(start=last_ds + pd.offsets.MonthBegin(1), periods=len(yhat), freq="MS")
    fc = pd.DataFrame({
        "ds": future_idx,
        "yhat": yhat.values
    })
    if conf is not None and not conf.empty:
        low_col = conf.columns[0]
        up_col  = conf.columns[1]
        fc["yhat_lower"] = conf[low_col].values
        fc["yhat_upper"] = conf[up_col].values
    return fc


def plot_forecast(history_df: pd.DataFrame,
                  fc_df: pd.DataFrame,
                  title: str,
                  out_png: Path):
    plt.figure(figsize=(11,5))
    plt.plot(history_df["ds"], history_df["y"], label="Actual", linewidth=2)
    if fc_df is not None and len(fc_df):
        plt.plot(fc_df["ds"], fc_df["yhat"], label="Forecast", linewidth=2)
        if "yhat_lower" in fc_df.columns and "yhat_upper" in fc_df.columns:
            plt.fill_between(fc_df["ds"], fc_df["yhat_lower"], fc_df["yhat_upper"], alpha=0.2, label="Conf. Interval")
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel("Revenue (€)")
    plt.legend()
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close()
