"""
EDA (Exploratory Data Analysis) Pipeline
=========================================
Part I: Statistics (General + Grouped by Churn)
Part II: 9 Visualizations

Input: data/processed/preprocessing_before_after.xlsx
  - Sheet "4b_After_FeatEng" for charts (readable values)
  - Sheet "5b_After_Scaling" for Heatmap (scaled values)
Output: eda_output/ folder with 9 PNG charts + 1 stats Excel
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg") # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

# ── Config ──────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.bbox"] = "tight"

OUTPUT_DIR = Path(__file__).parent / "eda_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Color palette
CHURN_PALETTE = {0: "#2ecc71", 1: "#e74c3c"} # Green = Stayed, Red = Churned
CHURN_LABELS = {0: "Stayed", 1: "Churned"}


# =============================================================================
# LOAD DATA
# =============================================================================

def load_data():
 """Load data from preprocessing_before_after.xlsx."""
 data_dir = Path(__file__).parent / "data" / "processed"
 bf_file = data_dir / "preprocessing_before_after.xlsx"

 if bf_file.exists():
  # Use Feature Engineered data (has new features, but NOT scaled)
  df_feat = pd.read_excel(bf_file, sheet_name="4b_After_FeatEng", engine="openpyxl")
  # Use Scaled data for heatmap
  df_scaled = pd.read_excel(bf_file, sheet_name="5b_After_Scaling", engine="openpyxl")
 else:
  # Fallback: run preprocessing on the raw data
  from utils.preprocessing import (
  DataCleaner, CategoricalEncoder, OutlierHandler,
  FeatureEngineer, FeatureScaler
  )
  xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
  df_raw = pd.read_excel(xlsx_files[-1], engine="openpyxl")
  df_feat = FeatureEngineer().fit_transform(
  OutlierHandler().fit_transform(
   CategoricalEncoder().fit_transform(
    DataCleaner().fit_transform(df_raw)
   )
  )
  )
  df_scaled = FeatureScaler().fit_transform(df_feat.copy())

 return df_feat, df_scaled


# =============================================================================
# PART I: STATISTICS
# =============================================================================

def generate_statistics(df: pd.DataFrame):
 """Generate descriptive and grouped statistics."""
 print("\n" + "=" * 60)
 print(" PART I: STATISTICS")
 print("=" * 60)

 stats_file = OUTPUT_DIR / "eda_statistics.xlsx"
 
 with pd.ExcelWriter(stats_file, engine="openpyxl") as writer:
  
  # ── 1. General Descriptive Stats ────────────────────────────
  numeric_cols = ["age", "balance", "credit_score", "tenure",
    "products_number", "rating"]
  cols_exist = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
  
  desc = df[cols_exist].describe().T
  desc["median"] = df[cols_exist].median()
  desc = desc[["count", "mean", "median", "std", "min", "25%", "50%", "75%", "max"]]
  desc.to_excel(writer, sheet_name="General_Stats")
  
  print("\n📌 1. General Descriptive Stats:")
  print(desc.to_string())
  
  # ── 2. Grouped Stats by Churn ───────────────────────────────
  if "churn" in df.columns:
   grouped = df.groupby("churn")[cols_exist].agg(["mean", "median", "std"])
   grouped.to_excel(writer, sheet_name="Grouped_by_Churn")
  
  print("\n📌 2. Grouped Stats (Churn vs Stayed):")
  # Simplified comparison table
  comparison = pd.DataFrame()
  for col in cols_exist:
   stayed_mean = df[df["churn"] == 0][col].mean()
   churn_mean = df[df["churn"] == 1][col].mean()
   diff_pct = ((churn_mean - stayed_mean) / stayed_mean * 100) if stayed_mean != 0 else 0
   comparison = pd.concat([comparison, pd.DataFrame({
    "Feature": [col],
    "Stayed (mean)": [f"{stayed_mean:.2f}"],
    "Churned (mean)": [f"{churn_mean:.2f}"],
    "Diff (%)": [f"{diff_pct:+.1f}%"]
   })], ignore_index=True)
  
  comparison.to_excel(writer, sheet_name="Churn_Comparison", index=False)
  print(comparison.to_string(index=False))
  
  # ── 3. Churn Rate Summary ───────────────────────────────
  churn_counts = df["churn"].value_counts()
  churn_rate = df["churn"].mean() * 100
  summary = pd.DataFrame({
   "Metric": ["Total Rows", "Stayed (0)", "Churned (1)", "Churn Rate (%)"],
   "Value": [len(df), churn_counts.get(0, 0), churn_counts.get(1, 0), f"{churn_rate:.2f}%"]
  })
  summary.to_excel(writer, sheet_name="Churn_Summary", index=False)
  
  print(f"\n📌 3. Churn Rate: {churn_rate:.2f}%")
  print(f" Stayed: {churn_counts.get(0, 0):,} | Churned: {churn_counts.get(1, 0):,}")
 
 print(f"\n Stats saved: {stats_file}")
 return stats_file


# =============================================================================
# PART II: VISUALIZATIONS
# =============================================================================

def chart_1_churn_pie(df):
 """1. Donut Chart: Overall Churn Rate."""
 fig, ax = plt.subplots(figsize=(8, 8))
 
 counts = df["churn"].value_counts()
 labels = [f"Stayed\n{counts[0]:,} ({counts[0]/len(df)*100:.1f}%)",
   f"Churned\n{counts[1]:,} ({counts[1]/len(df)*100:.1f}%)"]
 colors = [CHURN_PALETTE[0], CHURN_PALETTE[1]]
 
 wedges, texts = ax.pie(
  counts, labels=labels, colors=colors,
  startangle=90, wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
  textprops={"fontsize": 13, "fontweight": "bold"}
 )
 
 # Center text
 churn_rate = df["churn"].mean() * 100
 ax.text(0, 0, f"{churn_rate:.1f}%\nChurn", ha="center", va="center",
  fontsize=22, fontweight="bold", color="#e74c3c")
 
 ax.set_title("Overall Churn Rate", fontsize=16, fontweight="bold", pad=20)
 
 path = OUTPUT_DIR / "1_churn_pie.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 1: {path.name}")
 return path


def chart_2_churn_by_bank(df):
 """2. Stacked Bar: Churn Rate by Bank."""
 fig, ax = plt.subplots(figsize=(16, 8))
 
 # Calculate churn rate per bank
 bank_churn = df.groupby("bank_name")["churn"].agg(["mean", "count"]).reset_index()
 bank_churn.columns = ["bank_name", "churn_rate", "total"]
 bank_churn = bank_churn.sort_values("churn_rate", ascending=False)
 
 # Cross-tab for stacking
 ct = pd.crosstab(df["bank_name"], df["churn"], normalize="index") * 100
 ct = ct.loc[bank_churn["bank_name"]]
 
 ct.plot(kind="barh", stacked=True, color=[CHURN_PALETTE[0], CHURN_PALETTE[1]],
  ax=ax, edgecolor="white", linewidth=0.5)
 
 ax.set_xlabel("Percentage (%)", fontsize=12)
 ax.set_ylabel("")
 ax.set_title("Churn Rate by Bank (Sorted)", fontsize=16, fontweight="bold")
 ax.legend(["Stayed", "Churned"], loc="lower right", fontsize=11)
 ax.set_xlim(0, 100)
 
 # Add percentage labels
 for i, (_, row) in enumerate(ct.iterrows()):
  churn_pct = row.get(1, 0)
  if churn_pct > 3:
   ax.text(100 - churn_pct / 2, i, f"{churn_pct:.1f}%",
     ha="center", va="center", fontsize=8, color="white", fontweight="bold")
 
 plt.tight_layout()
 path = OUTPUT_DIR / "2_churn_by_bank.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 2: {path.name}")
 return path




def chart_7_month_trend(df):
 """7. Line Chart: Churn trend by review_month."""
 if "review_month" not in df.columns:
  print(" Chart 7: Skipped (review_month not found)")
  return None
 
 fig, ax = plt.subplots(figsize=(12, 6))
 
 monthly = df.groupby("review_month").agg(
  total=("churn", "count"),
  churned=("churn", "sum"),
  churn_rate=("churn", "mean")
 ).reset_index()
 monthly["churn_rate"] *= 100
 
 # Churn rate line
 ax.plot(monthly["review_month"], monthly["churn_rate"],
  color="#e74c3c", marker="o", linewidth=2.5, markersize=8, label="Churn Rate (%)")
 
 # Fill area
 ax.fill_between(monthly["review_month"], monthly["churn_rate"],
    alpha=0.15, color="#e74c3c")
 
 # Add data labels
 for _, row in monthly.iterrows():
  ax.text(row["review_month"], row["churn_rate"] + 0.5,
   f"{row['churn_rate']:.1f}%", ha="center", fontsize=10, fontweight="bold")
 
 ax.set_xlabel("Month", fontsize=13)
 ax.set_ylabel("Churn Rate (%)", fontsize=13)
 ax.set_title("Churn Rate Trend by Month", fontsize=15, fontweight="bold")
 ax.set_xticks(monthly["review_month"])
 ax.set_xticklabels([f"T{int(m)}" for m in monthly["review_month"]])
 ax.legend(fontsize=11)
 
 plt.tight_layout()
 path = OUTPUT_DIR / "7_month_trend.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 7: {path.name}")
 return path



 platform_cols = [c for c in df.columns if c.startswith("platform_")]
 if not platform_cols:
  print(" Chart 8: Skipped (platform columns not found)")
  return None

 fig, axes = plt.subplots(1, 2, figsize=(15, 6))

 # Reconstruct platform name from one-hot columns
 df_plot = df.copy()
 def get_platform(row):
  for c in platform_cols:
   if row[c] == 1:
    return c.replace("platform_", "").replace("_", " ").title()
  return "Unknown"
 df_plot["platform"] = df_plot.apply(get_platform, axis=1)

 # Left: Count by platform & churn
 ax1 = axes[0]
 platform_order = sorted(df_plot["platform"].unique())
 ct = pd.crosstab(df_plot["platform"], df_plot["churn"])
 ct.columns = ["Stayed", "Churned"]
 ct = ct.loc[platform_order]
 ct.plot(kind="bar", color=[CHURN_PALETTE[0], CHURN_PALETTE[1]], ax=ax1,
  edgecolor="white", linewidth=0.5, rot=0)
 ax1.set_title("Review Count by Platform", fontsize=13, fontweight="bold")
 ax1.set_xlabel("")
 ax1.set_ylabel("Count")

 # Right: Churn Rate per platform
 ax2 = axes[1]
 churn_rate = df_plot.groupby("platform")["churn"].mean().sort_values() * 100
 platform_colors = ["#3498db", "#9b59b6", "#e67e22"]
 bars = ax2.bar(churn_rate.index, churn_rate.values,
    color=platform_colors[:len(churn_rate)],
    edgecolor="white", width=0.5)

 for bar, val in zip(bars, churn_rate.values):
  ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
    f"{val:.1f}%", ha="center", fontsize=14, fontweight="bold")

 ax2.set_title("Churn Rate (%) by Platform", fontsize=13, fontweight="bold")
 ax2.set_ylabel("Churn Rate (%)")
 ax2.set_ylim(0, max(churn_rate.values) * 1.3)

 # Add avg line
 avg_rate = df_plot["churn"].mean() * 100
 ax2.axhline(y=avg_rate, color="#e74c3c", linestyle="--", linewidth=1.5, alpha=0.7)
 ax2.text(len(churn_rate) - 0.5, avg_rate + 0.3, f"Avg: {avg_rate:.1f}%",
   color="#e74c3c", fontsize=10, fontweight="bold")

 plt.tight_layout()
 path = OUTPUT_DIR / "8_platform_churn.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 8: {path.name}")
 return path


def chart_9_tenure_age_ratio(df):
 """9. KDE Density Plot: tenure_age_ratio by Churn group."""
 if "tenure_age_ratio" not in df.columns:
  print(" Chart 9: Skipped (tenure_age_ratio not found)")
  return None

 fig, axes = plt.subplots(1, 2, figsize=(16, 6))

 # Left: KDE density plot
 ax1 = axes[0]
 stayed = df[df["churn"] == 0]["tenure_age_ratio"]
 churned = df[df["churn"] == 1]["tenure_age_ratio"]

 sns.kdeplot(stayed, ax=ax1, color=CHURN_PALETTE[0], fill=True, alpha=0.4,
   linewidth=2, label=f"Stayed (mean={stayed.mean():.3f})")
 sns.kdeplot(churned, ax=ax1, color=CHURN_PALETTE[1], fill=True, alpha=0.4,
   linewidth=2, label=f"Churned (mean={churned.mean():.3f})")

 ax1.set_xlabel("Tenure / Age Ratio", fontsize=12)
 ax1.set_ylabel("Density", fontsize=12)
 ax1.set_title("Loyalty Ratio Distribution: Churned vs Stayed", fontsize=13, fontweight="bold")
 ax1.legend(fontsize=11)

 # Add mean lines
 ax1.axvline(stayed.mean(), color=CHURN_PALETTE[0], linestyle="--", linewidth=1.5, alpha=0.8)
 ax1.axvline(churned.mean(), color=CHURN_PALETTE[1], linestyle="--", linewidth=1.5, alpha=0.8)

 # Right: Boxplot comparison
 ax2 = axes[1]
 df_plot = df.copy()
 df_plot["churn_label"] = df_plot["churn"].map(CHURN_LABELS)
 sns.boxplot(data=df_plot, x="churn_label", y="tenure_age_ratio",
   palette=CHURN_PALETTE.values(), ax=ax2, width=0.5)

 # Add mean markers
 means = df_plot.groupby("churn_label")["tenure_age_ratio"].mean()
 for i, (label, mean_val) in enumerate(means.items()):
  ax2.scatter(i, mean_val, color="black", marker="D", s=60, zorder=5)
  ax2.text(i + 0.15, mean_val, f"Mean: {mean_val:.3f}",
    fontsize=10, va="center")

 ax2.set_xlabel("")
 ax2.set_ylabel("Tenure / Age Ratio")
 ax2.set_title("Loyalty Ratio: Churned vs Stayed", fontsize=13, fontweight="bold")

 plt.tight_layout()
 path = OUTPUT_DIR / "9_tenure_age_ratio.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 9: {path.name}")
 return path


def chart_10_age_distribution(df):
 """Phan phoi Tuoi (Age) - Histogram + KDE + Boxplot + IQR Whiskers."""
 fig, axes = plt.subplots(2, 1, figsize=(14, 10),
       gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
 
 age = df["age"].dropna()
 
 # --- Top: Histogram + KDE (hinh chuong) ---
 ax1 = axes[0]
 
 # Binning: [18, 30, 45, 60, 75]
 bin_edges = [18, 30, 45, 60, 75]
 
 sns.histplot(age, bins=25, kde=False, color="#3498db", alpha=0.4,
    stat="density", edgecolor="white", linewidth=0.5, ax=ax1,
    label="Histogram")
 
 # KDE (duong cong hinh chuong)
 sns.kdeplot(age, color="#e74c3c", linewidth=2.5, ax=ax1, label="KDE (Bell Curve)")
 
 # Tinh IQR de ve whiskers
 Q1 = age.quantile(0.25)
 Q3 = age.quantile(0.75)
 IQR = Q3 - Q1
 lower_fence = Q1 - 1.5 * IQR
 upper_fence = Q3 + 1.5 * IQR
 median = age.median()
 mean = age.mean()
 
 # Ve cac duong moc IQR
 ax1.axvline(Q1, color="#2ecc71", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Q1 = {Q1:.0f}")
 ax1.axvline(Q3, color="#2ecc71", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Q3 = {Q3:.0f}")
 ax1.axvline(median, color="#f39c12", linestyle="-", linewidth=2, alpha=0.9, label=f"Median = {median:.0f}")
 ax1.axvline(mean, color="#9b59b6", linestyle="-.", linewidth=1.5, alpha=0.8, label=f"Mean = {mean:.1f}")
 
 # Ve hang rao IQR (whiskers)
 ax1.axvline(lower_fence, color="#e74c3c", linestyle=":", linewidth=1.5, alpha=0.7, label=f"Lower Fence = {lower_fence:.0f}")
 ax1.axvline(upper_fence, color="#e74c3c", linestyle=":", linewidth=1.5, alpha=0.7, label=f"Upper Fence = {upper_fence:.0f}")
 
 # To mau vung an toan (trong IQR)
 ylim = ax1.get_ylim()
 ax1.axvspan(lower_fence, upper_fence, alpha=0.05, color="#2ecc71")
 
 # Ve moc nhom tuoi
 for b in bin_edges[1:-1]:
  ax1.axvline(b, color="gray", linestyle="-", linewidth=0.8, alpha=0.3)
  ax1.text(b, ylim[1] * 0.92, f"  {b}", color="gray", fontsize=9, va="top")
 
 ax1.set_title("Phan phoi Tuoi (Age Distribution)\nHistogram + KDE + IQR Outlier Boundaries", fontsize=15, fontweight="bold")
 ax1.set_ylabel("Density", fontsize=12)
 ax1.legend(fontsize=9, loc="upper right", framealpha=0.9)
 
 # --- Bottom: Boxplot ---
 ax2 = axes[1]
 bp = ax2.boxplot(age, vert=False, widths=0.6,
     patch_artist=True,
     boxprops=dict(facecolor="#3498db", alpha=0.5),
     medianprops=dict(color="#f39c12", linewidth=2),
     whiskerprops=dict(color="#e74c3c", linewidth=1.5),
     capprops=dict(color="#e74c3c", linewidth=1.5),
     flierprops=dict(marker="o", markerfacecolor="#e74c3c", markersize=4, alpha=0.5))
 
 ax2.set_xlabel("Age", fontsize=12)
 ax2.set_yticks([])
 ax2.set_title("Boxplot (IQR Whiskers)", fontsize=11)
 
 # Annotate Q1, Median, Q3
 for val, label in [(Q1, "Q1"), (median, "Med"), (Q3, "Q3")]:
  ax2.annotate(f"{label}={val:.0f}", xy=(val, 1), xytext=(val, 1.3),
     fontsize=9, ha="center", fontweight="bold",
     arrowprops=dict(arrowstyle="-", color="gray"))
 
 plt.tight_layout()
 path = OUTPUT_DIR / "10_age_distribution.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 10 Age Distribution: {path.name}")
 return path


def chart_11_balance_distribution(df):
 """Phan phoi So du (Balance) - Histogram + KDE + Boxplot + IQR Whiskers."""
 fig, axes = plt.subplots(2, 1, figsize=(14, 10),
       gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
 
 balance = df["balance"].dropna()
 balance_ty = balance / 1_000_000_000  # Doi sang ty VND
 
 # --- Top: Histogram + KDE (hinh chuong) ---
 ax1 = axes[0]
 
 # Binning: [0, 5, 10, 15, 20] ty VND
 bin_edges_ty = [0, 5, 10, 15, 20]
 
 sns.histplot(balance_ty, bins=30, kde=False, color="#2ecc71", alpha=0.4,
    stat="density", edgecolor="white", linewidth=0.5, ax=ax1,
    label="Histogram")
 
 # KDE (duong cong hinh chuong)
 sns.kdeplot(balance_ty, color="#e74c3c", linewidth=2.5, ax=ax1, label="KDE (Bell Curve)")
 
 # Tinh IQR
 Q1 = balance_ty.quantile(0.25)
 Q3 = balance_ty.quantile(0.75)
 IQR = Q3 - Q1
 lower_fence = max(0, Q1 - 1.5 * IQR)
 upper_fence = Q3 + 1.5 * IQR
 median = balance_ty.median()
 mean = balance_ty.mean()
 
 # Ve cac duong moc IQR
 ax1.axvline(Q1, color="#3498db", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Q1 = {Q1:.1f} ty")
 ax1.axvline(Q3, color="#3498db", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Q3 = {Q3:.1f} ty")
 ax1.axvline(median, color="#f39c12", linestyle="-", linewidth=2, alpha=0.9, label=f"Median = {median:.1f} ty")
 ax1.axvline(mean, color="#9b59b6", linestyle="-.", linewidth=1.5, alpha=0.8, label=f"Mean = {mean:.1f} ty")
 
 # Hang rao IQR (whiskers)
 ax1.axvline(lower_fence, color="#e74c3c", linestyle=":", linewidth=1.5, alpha=0.7, label=f"Lower Fence = {lower_fence:.1f} ty")
 ax1.axvline(upper_fence, color="#e74c3c", linestyle=":", linewidth=1.5, alpha=0.7, label=f"Upper Fence = {upper_fence:.1f} ty")
 
 # Vung an toan
 ylim = ax1.get_ylim()
 ax1.axvspan(lower_fence, upper_fence, alpha=0.05, color="#2ecc71")
 
 # Ve moc nhom so du
 for b in bin_edges_ty[1:-1]:
  ax1.axvline(b, color="gray", linestyle="-", linewidth=0.8, alpha=0.3)
  ax1.text(b, ylim[1] * 0.92, f"  {b} ty", color="gray", fontsize=9, va="top")
 
 ax1.set_title("Phan phoi So du (Balance Distribution)\nHistogram + KDE + IQR Outlier Boundaries", fontsize=15, fontweight="bold")
 ax1.set_ylabel("Density", fontsize=12)
 ax1.legend(fontsize=9, loc="upper right", framealpha=0.9)
 
 # --- Bottom: Boxplot ---
 ax2 = axes[1]
 bp = ax2.boxplot(balance_ty, vert=False, widths=0.6,
     patch_artist=True,
     boxprops=dict(facecolor="#2ecc71", alpha=0.5),
     medianprops=dict(color="#f39c12", linewidth=2),
     whiskerprops=dict(color="#e74c3c", linewidth=1.5),
     capprops=dict(color="#e74c3c", linewidth=1.5),
     flierprops=dict(marker="o", markerfacecolor="#e74c3c", markersize=4, alpha=0.5))
 
 ax2.set_xlabel("Balance (Ty VND)", fontsize=12)
 ax2.set_yticks([])
 ax2.set_title("Boxplot (IQR Whiskers)", fontsize=11)
 
 # Annotate
 for val, label in [(Q1, "Q1"), (median, "Med"), (Q3, "Q3")]:
  ax2.annotate(f"{label}={val:.1f}", xy=(val, 1), xytext=(val, 1.3),
     fontsize=9, ha="center", fontweight="bold",
     arrowprops=dict(arrowstyle="-", color="gray"))
 
 plt.tight_layout()
 path = OUTPUT_DIR / "11_balance_distribution.png"
 fig.savefig(path)
 plt.close(fig)
 print(f" Chart 11 Balance Distribution: {path.name}")
 return path


# =============================================================================
# MAIN
# =============================================================================

def main():
 print("\n" + "=" * 60)
 print("EDA (EXPLORATORY DATA ANALYSIS)")
 print("=" * 60)
 
 # Load both datasets
 # For charts 1-4, 6-7: use full preprocessed data (not scaled, readable values)
 # For chart 5 (heatmap): use scaled data
 
 data_dir = Path(__file__).parent / "data" / "processed"
 
 # Load full dataset through preprocessing pipeline (NOT scaled)
 from utils.preprocessing import (
  DataCleaner, CategoricalEncoder, OutlierHandler, FeatureEngineer, FeatureScaler
 )
 
 xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
 # Skip frozen files to use the latest Gaussian data
 xlsx_files = [f for f in xlsx_files if "FROZEN" not in f.name]
 df_raw = pd.read_excel(xlsx_files[-1], engine="openpyxl")
 print(f" Loaded: {xlsx_files[-1].name} ({df_raw.shape})")
 
 # Run pipeline steps (stop before scaling for readable charts)
 df = DataCleaner().fit_transform(df_raw)
 bank_name_original = df["bank_name"].copy()  # Save original names before encoding
 df = CategoricalEncoder().fit_transform(df)
 df = OutlierHandler().fit_transform(df)
 df = FeatureEngineer().fit_transform(df)
 df["bank_name"] = bank_name_original  # Restore real bank names for charts
 
 
 # -- Part I: Statistics --
 generate_statistics(df)
 
 # -- Part II: Visualizations --
 print("\n" + "=" * 60)
 print("PART II: VISUALIZATIONS")
 print("=" * 60)
 
 chart_1_churn_pie(df)
 chart_2_churn_by_bank(df)
 chart_7_month_trend(df)
 chart_10_age_distribution(df)
 chart_11_balance_distribution(df)

 
 print("\n" + "=" * 60)
 print(f" EDA COMPLETE!")
 print(f" All outputs saved to: {OUTPUT_DIR}")
 print("=" * 60)


if __name__ == "__main__":
 main()

