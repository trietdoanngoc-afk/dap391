"""
Export BEFORE/AFTER sample data for each preprocessing step.
Output: 1 Excel file with multiple sheets, each showing 10 rows.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from utils.preprocessing import (
 DataCleaner, CategoricalEncoder, OutlierHandler,
 FeatureEngineer, FeatureScaler
)


def main():
 # Load data
 data_dir = Path(__file__).parent / "data" / "processed"
 xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
 input_file = xlsx_files[-1]
 df = pd.read_excel(input_file, engine="openpyxl")

 # Take 10 sample rows (fixed index for consistency)
 sample_idx = [0, 1, 2, 3, 4, 100, 200, 500, 1000, 5000]
 N = 10

 output_dir = Path(__file__).parent / "eda_output" / "data" / "processed"
 output_dir.mkdir(parents=True, exist_ok=True)
 output_file = output_dir / "preprocessing_before_after.xlsx"

 with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

  # ---- Sheet 0: Original ----
  df.head(N).to_excel(writer, sheet_name="0_Original", index=False)

  # ---- Step 1: Data Cleaning ----
  df_before = df.head(N).copy()
  df_before.to_excel(writer, sheet_name="1a_Before_Cleaning", index=False)

  cleaner = DataCleaner()
  df_cleaned = cleaner.fit_transform(df.copy())
  df_cleaned.head(N).to_excel(writer, sheet_name="1b_After_Cleaning", index=False)

  # ---- Step 2: Categorical Encoding ----
  df_cleaned.head(N).to_excel(writer, sheet_name="2a_Before_Encoding", index=False)

  encoder = CategoricalEncoder()
  df_encoded = encoder.fit_transform(df_cleaned.copy())
  df_encoded.head(N).to_excel(writer, sheet_name="2b_After_Encoding", index=False)

  # ---- Step 3: Outlier Handling ----
  df_encoded.head(N).to_excel(writer, sheet_name="3a_Before_Outlier", index=False)

  outlier_handler = OutlierHandler(factor=1.5)
  df_outlier = outlier_handler.fit_transform(df_encoded.copy())
  df_outlier.head(N).to_excel(writer, sheet_name="3b_After_Outlier", index=False)

  # ---- Step 4: Feature Engineering ----
  df_outlier.head(N).to_excel(writer, sheet_name="4a_Before_FeatEng", index=False)

  engineer = FeatureEngineer()
  df_feat = engineer.fit_transform(df_outlier.copy())
  df_feat.head(N).to_excel(writer, sheet_name="4b_After_FeatEng", index=False)

  # ---- Step 5: Feature Scaling ----
  df_feat.head(N).to_excel(writer, sheet_name="5a_Before_Scaling", index=False)

  scaler = FeatureScaler(method="minmax")
  df_scaled = scaler.fit_transform(df_feat.copy())
  df_scaled.head(N).to_excel(writer, sheet_name="5b_After_Scaling", index=False)

 print(f" Saved: {output_file}")
 print(f" 12 sheets: Original + Before/After × 5 steps")


if __name__ == "__main__":
 main()
