"""
Run the full preprocessing pipeline and save output to a text file.
"""

import sys
from pathlib import Path
import io

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from utils.preprocessing import preprocess_full_pipeline


def main():
 data_dir = Path(__file__).parent / "data" / "processed"
 xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
 
 if not xlsx_files:
  print("No data file found")
  return
 
 input_file = xlsx_files[-1]
 df = pd.read_excel(input_file, engine="openpyxl")
 
 # Capture all output
 old_stdout = sys.stdout
 sys.stdout = buffer = io.StringIO()
 
 print(f" Input: {input_file.name}")
 print(f" Original shape: {df.shape}")
 
 df_processed = preprocess_full_pipeline(df)
 
 print(f"\n📋 Final columns ({len(df_processed.columns)}):")
 for col in df_processed.columns:
  print(f" • {col}: {df_processed[col].dtype}")
 
 print(f"\n Sample data (first 3 rows):")
 pd.set_option('display.max_columns', None)
 pd.set_option('display.width', 200)
 print(df_processed.head(3).to_string())
 
 sys.stdout = old_stdout
 output = buffer.getvalue()
 
 with open("preprocessing_output.txt", "w", encoding="utf-8") as f:
  f.write(output)
 
 print(output)
 print("\n Output saved to preprocessing_output.txt")


if __name__ == "__main__":
 main()
