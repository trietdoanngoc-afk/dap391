"""
Demo: Preprocessing Pipeline Step-by-Step
Shows BEFORE and AFTER for each step.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from utils.preprocessing import (
 DataCleaner, CategoricalEncoder, OutlierHandler, 
 FeatureEngineer, FeatureScaler
)


def separator(title):
 return f"\n{'='*70}\n {title}\n{'='*70}"


def show_before_after(label, col_name, before_df, after_df, n=5):
 """Show before/after comparison for a specific column."""
 lines = []
 lines.append(f"\n {label}: '{col_name}'")
 
 if col_name in before_df.columns and col_name in after_df.columns:
  # Side by side
  lines.append(f" {'BEFORE':<30} {'AFTER':<30}")
  lines.append(f" {'-'*28} {'-'*28}")
  for i in range(min(n, len(before_df))):
   b = str(before_df[col_name].iloc[i])
   a = str(after_df[col_name].iloc[i])
   lines.append(f" {b:<30} {a:<30}")
 elif col_name in before_df.columns:
  lines.append(f" BEFORE: {before_df[col_name].head(n).tolist()}")
  lines.append(f" AFTER: [DROPPED]")
 elif col_name in after_df.columns:
  lines.append(f" BEFORE: [NOT EXISTS]")
  lines.append(f" AFTER: {after_df[col_name].head(n).tolist()}")
 
 return "\n".join(lines)


def main():
 # Load data
 data_dir = Path(__file__).parent / "data" / "processed"
 xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
 input_file = xlsx_files[-1]
 
 df_original = pd.read_excel(input_file, engine="openpyxl")
 output = []
 
 output.append(separator(" ORIGINAL DATA"))
 output.append(f"\n Shape: {df_original.shape}")
 output.append(f" Columns: {list(df_original.columns)}")
 output.append(f"\n Sample (5 rows):")
 output.append(df_original.head().to_string(max_cols=8))
 
 # =========================================================================
 # STEP 1: DATA CLEANING
 # =========================================================================
 output.append(separator("📌 STEP 1: DATA CLEANING"))
 output.append("""
 Phương pháp:
 • Drop Duplicates - Xóa hàng trùng lặp hoàn toàn
 • Handle Missing Values - Fill median (số) / mode (chữ)
 • Fix Dtypes - date: str → datetime
 • Drop Irrelevant - Xóa review_id (không giúp dự đoán)
 
 Vì sao: Dữ liệu bẩn → model học sai → dự đoán sai
""")
 
 df_before = df_original.copy()
 cleaner = DataCleaner()
 df_after_clean = cleaner.fit_transform(df_before)
 
 output.append(show_before_after("Drop ID column", "review_id", df_before, df_after_clean))
 output.append(f"\n Fix Dtypes: 'date'")
 output.append(f" {'BEFORE':<30} {'AFTER':<30}")
 output.append(f" {'-'*28} {'-'*28}")
 if 'date' in df_before.columns and 'date' in df_after_clean.columns:
  output.append(f" {str(df_before['date'].dtype):<30} {str(df_after_clean['date'].dtype):<30}")
  output.append(f" {str(df_before['date'].iloc[0]):<30} {str(df_after_clean['date'].iloc[0]):<30}")
 else:
  output.append(" Date column not present in both.")
 
 output.append(f"\n Shape: {df_before.shape} → {df_after_clean.shape}")
 
 # =========================================================================
 # STEP 2: CATEGORICAL ENCODING
 # =========================================================================
 output.append(separator("📌 STEP 2: CATEGORICAL ENCODING"))
 output.append("""
 Phương pháp:
 • Binary Encoding (sex) - Male=1, Female=0
  → Vì: Chỉ 2 giá trị, 0/1 là đủ
 • One-Hot Encoding (platform) - Tạo 3 cột dummy
  → Vì: 3 giá trị KHÔNG có thứ tự (app_store ≠ "lớn hơn" facebook)
 • Label Encoding (bank_name) - Gán mỗi bank 1 số (0-34)
  → Vì: 35 giá trị, One-Hot tạo 35 cột → quá nhiều
 
 Vì sao: ML models chỉ hiểu số, không hiểu chữ
""")
 
 df_before_encode = df_after_clean.copy()
 encoder = CategoricalEncoder()
 df_after_encode = encoder.fit_transform(df_before_encode)
 
 output.append(show_before_after("Binary Encoding", "sex", df_before_encode, df_after_encode, 8))
 
 output.append(f"\n One-Hot Encoding: 'platform' → 3+ cột")
 output.append(f" {'BEFORE (platform)':<30} {'AFTER (3 cột dummy)':<50}")
 output.append(f" {'-'*28} {'-'*48}")
 for i in range(min(5, len(df_before_encode))):
  if 'platform' in df_before_encode.columns:
   b = str(df_before_encode['platform'].iloc[i])
   a1 = df_after_encode.get('platform_app_store', pd.Series([False]*len(df_after_encode))).iloc[i]
   a2 = df_after_encode.get('platform_facebook', pd.Series([False]*len(df_after_encode))).iloc[i]
   a3 = df_after_encode.get('platform_google_play', pd.Series([False]*len(df_after_encode))).iloc[i]
   output.append(f" {b:<30} app_store={a1} facebook={a2} google_play={a3}")
 
 output.append(show_before_after("Label Encoding", "bank_name", df_before_encode, df_after_encode, 8))
 
 output.append(f"\n Shape: {df_before_encode.shape} → {df_after_encode.shape}")
 
 # =========================================================================
 # STEP 3: OUTLIER HANDLING
 # =========================================================================
 output.append(separator("📌 STEP 3: OUTLIER HANDLING (IQR)"))
 output.append("""
 Phương pháp: IQR (Interquartile Range)
 • Q1 = percentile 25%, Q3 = percentile 75%
 • IQR = Q3 - Q1
 • Lower = Q1 - 1.5×IQR, Upper = Q3 + 1.5×IQR
 • Giá trị ngoài [Lower, Upper] → CAP về biên gần nhất
 
 Vì sao dùng IQR: Robust (không bị ảnh hưởng bởi outlier)
 Vì sao Capping: Giữ nguyên số lượng data, chỉ điều chỉnh giá trị cực đoan
""")
 
 df_before_outlier = df_after_encode.copy()
 outlier_handler = OutlierHandler(factor=1.5)
 df_after_outlier = outlier_handler.fit_transform(df_before_outlier)
 
 for col in ["age", "credit_score", "balance", "tenure"]:
  if col in df_before_outlier.columns:
   bounds = outlier_handler.bounds.get(col, {})
   output.append(f"\n '{col}': Q1={bounds.get('Q1',0):.0f}, Q3={bounds.get('Q3',0):.0f}, IQR={bounds.get('IQR',0):.0f}")
   output.append(f" Bounds: [{bounds.get('lower',0):.0f}, {bounds.get('upper',0):.0f}]")
   output.append(f" {'BEFORE':<35} {'AFTER':<35}")
   output.append(f" {'-'*33} {'-'*33}")
   output.append(f" min={df_before_outlier[col].min():<28.0f} min={df_after_outlier[col].min():<28.0f}")
   output.append(f" max={df_before_outlier[col].max():<28.0f} max={df_after_outlier[col].max():<28.0f}")
   output.append(f" mean={df_before_outlier[col].mean():<27.1f} mean={df_after_outlier[col].mean():<27.1f}")
 
 output.append(f"\n Shape: {df_before_outlier.shape} → {df_after_outlier.shape}")
 
 # =========================================================================
 # STEP 4: FEATURE ENGINEERING
 # =========================================================================
 output.append(separator("📌 STEP 4: FEATURE ENGINEERING"))
 output.append("""
 Phương pháp: Tạo features mới từ features có sẵn
 • balance_per_product = balance / products_number
  → Đo giá trị TB mỗi sản phẩm
 • tenure_age_ratio = tenure / age
  → Tỷ lệ trung thành so với tuổi
 • is_high_value = (balance > median) AND (credit_score > 600)
  → Phân khúc khách hàng VIP
 • review_month, review_day_of_week = extract từ date
  → Phát hiện xu hướng theo mùa/ngày
 
 Vì sao: Tạo thêm thông tin model không tự suy ra → cải thiện accuracy
""")
 
 df_before_feat = df_after_outlier.copy()
 engineer = FeatureEngineer()
 df_after_feat = engineer.fit_transform(df_before_feat)
 
 new_features = ["balance_per_product", "tenure_age_ratio", "is_high_value", "review_month", "review_day_of_week"]
 for feat in new_features:
  if feat in df_after_feat.columns:
   output.append(f"\n NEW FEATURE: '{feat}'")
   output.append(f" Sample values: {df_after_feat[feat].head(5).tolist()}")
 
 output.append(f"\n Dropped: 'date' → replaced by review_month + review_day_of_week")
 output.append(f"\n Shape: {df_before_feat.shape} → {df_after_feat.shape} (+{df_after_feat.shape[1]-df_before_feat.shape[1]} features)")
 
 # =========================================================================
 # STEP 5: FEATURE SCALING
 # =========================================================================
 output.append(separator("📌 STEP 5: FEATURE SCALING (MinMaxScaler)"))
 output.append("""
 Phương pháp: MinMaxScaler
 • Công thức: X_scaled = (X - X_min) / (X_max - X_min)
 • Kết quả: Tất cả giá trị trong khoảng [0, 1]
 
 Vì sao: age (18-70) vs balance (0-2B) → model ưu tiên balance
 Scale giúp model đánh giá công bằng tất cả features
 
 KHÔNG scale: churn (target), credit_card, active_member, is_high_value, platform_*
""")
 
 df_before_scale = df_after_feat.copy()
 scaler = FeatureScaler(method="minmax")
 df_after_scale = scaler.fit_transform(df_before_scale)
 
 scale_cols = ["age", "tenure", "credit_score", "balance", "rating", "balance_per_product"]
 for col in scale_cols:
  if col in df_before_scale.columns and col in df_after_scale.columns:
   output.append(f"\n '{col}':")
   output.append(f" {'BEFORE':<40} {'AFTER (scaled 0-1)':<40}")
   output.append(f" {'-'*38} {'-'*38}")
   for i in range(min(3, len(df_before_scale))):
    b = f"{df_before_scale[col].iloc[i]:.2f}"
    a = f"{df_after_scale[col].iloc[i]:.6f}"
    output.append(f" {b:<40} {a:<40}")
   output.append(f" min={df_before_scale[col].min():.2f}, max={df_before_scale[col].max():.2f} → min={df_after_scale[col].min():.6f}, max={df_after_scale[col].max():.6f}")
 
 output.append(f"\n Shape: {df_before_scale.shape} → {df_after_scale.shape}")
 
 # =========================================================================
 # FINAL SUMMARY
 # =========================================================================
 output.append(separator(" FINAL SUMMARY"))
 output.append(f"\n Original: {df_original.shape[0]:,} rows × {df_original.shape[1]} columns")
 output.append(f" Final: {df_after_scale.shape[0]:,} rows × {df_after_scale.shape[1]} columns")
 output.append(f"\n Columns before: {list(df_original.columns)}")
 output.append(f" Columns after: {list(df_after_scale.columns)}")
 
 # Write to file
 full_output = "\n".join(output)
 output_file = Path(__file__).parent / "preprocessing_demo.txt"
 with open(output_file, "w", encoding="utf-8") as f:
  f.write(full_output)
 
 print(full_output)
 print(f"\n Demo saved to: {output_file}")


if __name__ == "__main__":
 main()
