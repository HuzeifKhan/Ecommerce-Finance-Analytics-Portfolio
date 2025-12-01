# 03_Analysis/ml/churn_models.py
"""
Phase 10 – Customer Churn Prediction (Classification)

Data source:
    01_Data/processed/transactions.csv

Expected columns:
    - CustomerID
    - InvoiceDate
    - LineAmount
    - IsReturn   (0 = normal sale, 1 = return)  [if present]

Goal:
    Build a churn label and train classification models to predict
    which customers are likely to be "churned" (inactive).

Definition (simple, interpretable):
    - Recency = days since last purchase at snapshot_date
    - If Recency > CHURN_THRESHOLD_DAYS  -> Churned = 1
      else                                Churned = 0

Models:
    - Logistic Regression (baseline, interpretable)
    - Random Forest Classifier (non-linear, robust)

Outputs:
    - 03_Analysis/ml_outputs/churn_ml_metrics.json
    - 03_Analysis/ml_outputs/churn_rf_feature_importance.png
    - 03_Analysis/ml_outputs/churn_rf_roc_curve.png
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]   # repo root

DATA_DIR = BASE_DIR / "01_Data" / "processed"
ANALYSIS_DIR = BASE_DIR / "03_Analysis"
ML_OUTPUT_DIR = ANALYSIS_DIR / "ml_outputs"

ML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------
# Churn definition threshold: if no purchase in > N days → churned
CHURN_THRESHOLD_DAYS = 90


# -------------------------------------------------------------------
# Data loading & feature table
# -------------------------------------------------------------------
def load_transactions() -> pd.DataFrame:
    """
    Load cleaned transactions from 01_Data/processed/transactions.csv.
    Same structure as used in Phase 9 (CLV ML).
    """
    path = DATA_DIR / "transactions.csv"
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path}")

    print(f"Loading transactions from: {path}")

    df = pd.read_csv(path)

    expected_cols = {"CustomerID", "InvoiceDate", "LineAmount"}
    missing = expected_cols.difference(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns in transactions.csv: {missing}")

    df = df.copy()
    df = df.dropna(subset=["CustomerID"])

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(str)

    if "IsReturn" in df.columns:
        df = df[df["IsReturn"] == 0]

    df["Revenue"] = df["LineAmount"]

    return df


def build_customer_level_table_for_churn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build customer-level features and churn label.

    Features:
        RecencyDays      = days since last purchase
        Frequency        = number of transactions
        Monetary         = total Revenue
        TenureDays       = days between first and last purchase + 1
        AvgOrderValue    = Monetary / Frequency
        OrdersPerMonth   = Frequency / (TenureDays / 30)

    Target:
        Churned (0/1) based on RecencyDays > CHURN_THRESHOLD_DAYS
    """
    max_date = df["InvoiceDate"].max()
    snapshot_date = max_date + pd.Timedelta(days=1)

    grp = df.groupby("CustomerID")

    last_date = grp["InvoiceDate"].max()
    first_date = grp["InvoiceDate"].min()
    recency_days = (snapshot_date - last_date).dt.days
    tenure_days = (last_date - first_date).dt.days + 1

    frequency = grp.size()
    monetary = grp["Revenue"].sum()

    # Avoid division by zero
    avg_order_value = monetary / frequency.replace(0, np.nan)
    orders_per_month = frequency / (tenure_days.replace(0, np.nan) / 30.0)

    churned = (recency_days > CHURN_THRESHOLD_DAYS).astype(int)

    cust_df = pd.DataFrame(
        {
            "CustomerID": recency_days.index,
            "RecencyDays": recency_days.values,
            "Frequency": frequency.values,
            "Monetary": monetary.values,
            "TenureDays": tenure_days.values,
            "AvgOrderValue": avg_order_value.values,
            "OrdersPerMonth": orders_per_month.values,
            "Churned": churned.values,
        }
    )

    cust_df = cust_df.dropna()

    print("Churn distribution (0=active, 1=churned):")
    print(cust_df["Churned"].value_counts(normalize=True).rename("share"))

    return cust_df


# -------------------------------------------------------------------
# ML preparation & evaluation
# -------------------------------------------------------------------
def build_ml_data(cust_df: pd.DataFrame):
    target_col = "Churned"
    feature_cols = [
        "RecencyDays",
        "Frequency",
        "Monetary",
        "TenureDays",
        "AvgOrderValue",
        "OrdersPerMonth",
    ]

    X = cust_df[feature_cols]
    y = cust_df[target_col]

    scaler = StandardScaler()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    return scaler, X_train, X_test, y_train, y_test, feature_cols


def evaluate_classifier(name, model, X_test, y_test):
    y_pred = model.predict(X_test)

    # Some classifiers (like RF) support predict_proba; Logistic does as well.
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_prob)
    else:
        # fallback: use decision_function if available, else None
        if hasattr(model, "decision_function"):
            scores = model.decision_function(X_test)
            roc_auc = roc_auc_score(y_test, scores)
        else:
            roc_auc = float("nan")

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    return {
        "model": name,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
    }


def plot_feature_importance_rf(model: Pipeline, feature_names, save_path: Path):
    """
    Plot RandomForest feature importances.
    """
    rf = model.named_steps["classifier"]
    importances = rf.feature_importances_
    idx = np.argsort(importances)[::-1]

    sorted_features = np.array(feature_names)[idx]
    sorted_importances = importances[idx]

    plt.figure(figsize=(8, 5))
    plt.barh(sorted_features[::-1], sorted_importances[::-1])
    plt.xlabel("Importance")
    plt.title("Random Forest – Churn Feature Importance")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_roc_curve(model: Pipeline, X_test, y_test, save_path: Path, title: str):
    """
    Plot ROC curve for a classifier.
    """
    if not hasattr(model, "predict_proba"):
        print("Model does not support predict_proba; skipping ROC curve.")
        return

    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc_score(y_test, y_prob):.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Random baseline")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
def main():
    print("▶ Phase 10 – Churn ML models: starting...")

    df = load_transactions()
    print(f"Loaded {len(df):,} transaction rows")

    cust_df = build_customer_level_table_for_churn(df)
    print(f"Built customer table with {len(cust_df):,} customers")

    scaler, X_train, X_test, y_train, y_test, feature_names = build_ml_data(cust_df)

    metrics = {}

    # 1) Logistic Regression
    log_reg_pipeline = Pipeline(
        steps=[
            ("scaler", scaler),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    log_reg_pipeline.fit(X_train, y_train)
    metrics["LogisticRegression"] = evaluate_classifier(
        "LogisticRegression", log_reg_pipeline, X_test, y_test
    )

    # 2) Random Forest
    rf_pipeline = Pipeline(
        steps=[
            ("scaler", scaler),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=250,
                    random_state=42,
                    n_jobs=-1,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    rf_pipeline.fit(X_train, y_train)
    metrics["RandomForestClassifier"] = evaluate_classifier(
        "RandomForestClassifier", rf_pipeline, X_test, y_test
    )

    # Save metrics
    metrics_path = ML_OUTPUT_DIR / "churn_ml_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Metrics saved to {metrics_path}")

    # Feature importance for RF
    fi_path = ML_OUTPUT_DIR / "churn_rf_feature_importance.png"
    plot_feature_importance_rf(
        model=rf_pipeline,
        feature_names=feature_names,
        save_path=fi_path,
    )
    print(f"📊 Feature importance plot saved to {fi_path}")

    # ROC curve for RF
    roc_path = ML_OUTPUT_DIR / "churn_rf_roc_curve.png"
    plot_roc_curve(
        model=rf_pipeline,
        X_test=X_test,
        y_test=y_test,
        save_path=roc_path,
        title="Random Forest – Churn ROC Curve",
    )
    print(f"📈 ROC curve saved to {roc_path}")

    print("🎉 Phase 10 – Churn ML models completed.")


if __name__ == "__main__":
    main()
