# 03_Analysis/ml/clv_ml_models.py
"""
Phase 9 – CLV Prediction (ML Section) – RFM-based (transactions.csv)

Data source:
    01_Data/processed/transactions.csv

Expected columns:
    - CustomerID
    - InvoiceDate
    - LineAmount
    - IsReturn   (0 = normal sale, 1 = return)  [if present]

We build customer-level features:
    - Recency (days since last purchase)
    - Frequency (number of transactions)
    - Monetary (total LineAmount, returns removed)

Target:
    - CLV = total LineAmount per customer (over entire period)

Models:
    - Linear Regression
    - Random Forest Regressor

Outputs:
    03_Analysis/ml_outputs/clv_ml_metrics.json
    03_Analysis/ml_outputs/clv_rf_feature_importance.png
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]   # repo root

DATA_DIR = BASE_DIR / "01_Data" / "processed"
ANALYSIS_DIR = BASE_DIR / "03_Analysis"
ML_OUTPUT_DIR = ANALYSIS_DIR / "ml_outputs"

ML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# Data loading & feature table
# -------------------------------------------------------------------
def load_transactions() -> pd.DataFrame:
    """
    Load cleaned transactions from 01_Data/processed/transactions.csv.
    """

    # We know from your folder that it's transactions.csv
    path = DATA_DIR / "transactions.csv"
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}")

    print(f"Loading transactions from: {path}")

    df = pd.read_csv(path)

    # basic sanity checks
    expected_cols = {"CustomerID", "InvoiceDate", "LineAmount"}
    missing = expected_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in transactions.csv: {missing}")

    df = df.copy()
    df = df.dropna(subset=["CustomerID"])

    # ensure types
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(str)

    # drop returns if IsReturn exists
    if "IsReturn" in df.columns:
        df = df[df["IsReturn"] == 0]

    # rename LineAmount -> Revenue for clarity
    df["Revenue"] = df["LineAmount"]

    return df


def build_customer_level_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level data to customer-level RFM + CLV.

    Features:
        Recency      = days since last purchase
        Frequency    = number of transactions (rows) per customer
        Monetary     = total Revenue
    Target:
        CLV          = Monetary
    """

    max_date = df["InvoiceDate"].max()
    snapshot_date = max_date + pd.Timedelta(days=1)

    grp = df.groupby("CustomerID")

    recency = (snapshot_date - grp["InvoiceDate"].max()).dt.days
    frequency = grp.size()
    monetary = grp["Revenue"].sum()

    clv = monetary.copy()

    cust_df = pd.DataFrame(
        {
            "CustomerID": recency.index,
            "Recency": recency.values,
            "Frequency": frequency.values,
            "Monetary": monetary.values,
            "CLV": clv.values,
        }
    )

    # drop any weird NaNs
    cust_df = cust_df.dropna(subset=["CLV", "Recency", "Frequency", "Monetary"])

    return cust_df


# -------------------------------------------------------------------
# ML preparation & evaluation
# -------------------------------------------------------------------
def build_ml_data(cust_df: pd.DataFrame):
    target_col = "CLV"
    feature_cols = ["Recency", "Frequency", "Monetary"]

    X = cust_df[feature_cols]
    y = cust_df[target_col]

    numeric_features = feature_cols

    # Simple numeric pipeline: scale -> model
    scaler = StandardScaler()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return scaler, X_train, X_test, y_train, y_test, numeric_features


def evaluate_model(name, model, X_test, y_test):
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)

    # Older scikit-learn versions don't support `squared=False`,
    # so we compute RMSE manually: sqrt(MSE)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5

    r2 = r2_score(y_test, y_pred)

    return {
        "model": name,
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
    }


def plot_feature_importance_rf(
    model: Pipeline,
    feature_names,
    save_path: Path,
):
    """
    Plot RandomForest feature importances for numeric features.
    """
    rf = model.named_steps["regressor"]
    importances = rf.feature_importances_
    idx = np.argsort(importances)[::-1]

    sorted_features = np.array(feature_names)[idx]
    sorted_importances = importances[idx]

    plt.figure(figsize=(8, 5))
    plt.barh(sorted_features[::-1], sorted_importances[::-1])
    plt.xlabel("Importance")
    plt.title("Random Forest Feature Importance (RFM Features)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main():
    print("▶ Phase 9 – CLV ML models: starting...")

    df = load_transactions()
    print(f"Loaded {len(df):,} transaction rows")

    cust_df = build_customer_level_table(df)
    print(f"Built customer table with {len(cust_df):,} customers")

    scaler, X_train, X_test, y_train, y_test, feature_names = build_ml_data(cust_df)

    # -----------------------
    # 1) Linear Regression
    # -----------------------
    lr_pipeline = Pipeline(
        steps=[
            ("scaler", scaler),
            ("regressor", LinearRegression()),
        ]
    )

    lr_pipeline.fit(X_train, y_train)
    lr_metrics = evaluate_model("LinearRegression", lr_pipeline, X_test, y_test)

    # -----------------------
    # 2) Random Forest
    # -----------------------
    rf_pipeline = Pipeline(
        steps=[
            ("scaler", scaler),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    rf_pipeline.fit(X_train, y_train)
    rf_metrics = evaluate_model(
        "RandomForestRegressor", rf_pipeline, X_test, y_test
    )

    metrics = {
        "LinearRegression": lr_metrics,
        "RandomForestRegressor": rf_metrics,
    }

    metrics_path = ML_OUTPUT_DIR / "clv_ml_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Metrics saved to {metrics_path}")

    fi_path = ML_OUTPUT_DIR / "clv_rf_feature_importance.png"
    plot_feature_importance_rf(
        model=rf_pipeline,
        feature_names=feature_names,
        save_path=fi_path,
    )
    print(f"📊 Feature importance plot saved to {fi_path}")

    print("🎉 Phase 9 – CLV ML models completed.")


if __name__ == "__main__":
    main()

