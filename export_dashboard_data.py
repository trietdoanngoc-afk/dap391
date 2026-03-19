"""
Export preprocessed data to JSON for the interactive dashboard.
Outputs: dashboard/data.json

Performance: Uses pre-aggregated compact arrays for charts.
- agg: ~5,000 groups instead of 45,500 raw records
- at_risk / near_risk: capped for table display
"""

import sys
import json
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from utils.preprocessing import (
    DataCleaner, CategoricalEncoder, OutlierHandler, FeatureEngineer
)


def assign_priority(row):
    if row["rating"] == 1 and row["balance"] > 1_000_000_000:
        return "high"
    elif row["rating"] == 2 or (row["rating"] == 1 and row["balance"] >= 500_000_000):
        return "medium"
    else:
        return "low"


def main():
    data_dir = Path(__file__).parent / "data" / "processed"
    xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
    raw = pd.read_excel(xlsx_files[-1], engine="openpyxl")
    print(f"📂 Loaded: {xlsx_files[-1].name} ({raw.shape})")

    df_raw = raw.copy()

    # Preprocessing pipeline (stop before scaling)
    df = DataCleaner().fit_transform(raw)
    df = CategoricalEncoder().fit_transform(df)
    df = OutlierHandler().fit_transform(df)
    df = FeatureEngineer().fit_transform(df)

    # Reconstruct platform (vectorized for speed)
    platform_cols = [c for c in df.columns if c.startswith("platform_")]
    df["platform"] = "Unknown"
    for c in platform_cols:
        name = c.replace("platform_", "").replace("_", " ").title()
        df.loc[df[c] == 1, "platform"] = name

    # ── Build JSON ───────────────────────────────────────────────────────

    data = {}

    # 1. KPIs
    data["kpi"] = {
        "total_customers": int(len(df)),
        "churn_rate": round(float(df["churn"].mean() * 100), 1),
        "avg_rating": round(float(df["rating"].mean()), 1),
        "total_churned": int(df["churn"].sum()),
    }

    # 2. Filter options
    banks = sorted(df_raw["bank_name"].unique().tolist())
    platforms = sorted(df["platform"].unique().tolist())
    data["banks"] = banks
    data["platforms"] = platforms

    # 3. PRE-AGGREGATED data for charts (compact arrays)
    #    Format: [bank, platform, rating, vip, month, churn, count, sum_balance, sum_tenure]
    platform_to_idx = {p: i for i, p in enumerate(platforms)}
    df["platform_idx"] = df["platform"].map(platform_to_idx).astype(int)
    df["vip"] = df["is_high_value"].astype(int) if "is_high_value" in df.columns else 0

    agg_df = df.groupby(
        ["bank_name", "platform_idx", "rating", "vip", "review_month", "churn"]
    ).agg(
        count=("churn", "size"),
        sum_balance=("balance", "sum"),
        sum_tenure=("tenure", "sum"),
    ).reset_index()

    data["agg"] = agg_df.values.tolist()
    # Convert numpy types to native Python
    data["agg"] = [[int(v) for v in row] for row in data["agg"]]

    print(f"   Aggregate groups: {len(data['agg']):,} (was {len(df):,} records)")

    # 4. At-risk customers (rating <= 2) with priority tags
    at_risk_df = df_raw[df_raw["rating"] <= 2].copy()
    at_risk_list = []
    for _, row in at_risk_df.iterrows():
        balance = int(row.get("balance", 0))
        priority = assign_priority(row)
        at_risk_list.append({
            "bank": str(row.get("bank_name", "")),
            "rating": int(row["rating"]),
            "churn": int(row["churn"]),
            "platform": str(row.get("platform", "")).replace("_", " ").title(),
            "age": int(row.get("age", 0)),
            "balance": balance,
            "credit_score": int(row.get("credit_score", 0)),
            "tenure": int(row.get("tenure", 0)),
            "priority": priority,
        })

    priority_order = {"high": 0, "medium": 1, "low": 2}
    at_risk_list.sort(key=lambda x: (priority_order[x["priority"]], -x["balance"]))

    # Pre-compute priority counts from FULL list
    data["priority_counts"] = {
        "high": sum(1 for x in at_risk_list if x["priority"] == "high"),
        "medium": sum(1 for x in at_risk_list if x["priority"] == "medium"),
        "low": sum(1 for x in at_risk_list if x["priority"] == "low"),
    }
    # Balanced sampling: top N from each priority for table display
    cap = 200
    capped = []
    for p in ["high", "medium", "low"]:
        group = [x for x in at_risk_list if x["priority"] == p]
        capped.extend(group[:cap])
    data["at_risk"] = capped
    data["at_risk_total"] = len(at_risk_list)

    # 5. Near-risk: rating 3, still active (capped for performance)
    near_risk_df = df_raw[(df_raw["rating"] == 3) & (df_raw["churn"] == 0)].copy()
    near_risk_list = []
    for _, row in near_risk_df.iterrows():
        near_risk_list.append({
            "bank": str(row.get("bank_name", "")),
            "rating": 3,
            "churn": 0,
            "platform": str(row.get("platform", "")).replace("_", " ").title(),
            "age": int(row.get("age", 0)),
            "balance": int(row.get("balance", 0)),
            "credit_score": int(row.get("credit_score", 0)),
            "tenure": int(row.get("tenure", 0)),
        })
    near_risk_list.sort(key=lambda x: -x["balance"])
    data["near_risk"] = near_risk_list[:500]
    data["near_risk_total"] = len(near_risk_list)

    # Output
    out_dir = Path(__file__).parent / "dashboard"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "data.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    size_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"✅ Exported: {out_file} ({size_mb:.1f} MB)")
    print(f"   At-risk: {data['at_risk_total']:,} (table: {len(data['at_risk'])})")
    pc = data["priority_counts"]
    print(f"     🔴 High: {pc['high']:,} | 🟠 Medium: {pc['medium']:,} | 🟡 Low: {pc['low']:,}")
    print(f"   Near-risk: {data['near_risk_total']:,} (table: {len(data['near_risk'])})")


if __name__ == "__main__":
    main()
