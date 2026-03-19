"""
Main script to run all crawlers and generate data.
Optimized for performance and parallel execution.
"""

import sys
from pathlib import Path
import time
import pandas as pd
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import FINAL_COLUMNS, TIDB_CONFIG
from crawlers import run_all_crawlers
from utils import add_synthetic_customer_features


def push_to_tidb(df: pd.DataFrame):
    """Push DataFrame to TiDB Cloud database."""
    cfg = TIDB_CONFIG
    
    connection_string = (
        f"mysql+mysqlconnector://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    
    ssl_args = {
        "ssl_ca": cfg["ca_path"],
        "ssl_verify_cert": True,
    }
    
    print(f"   -> Connecting to TiDB Cloud ({cfg['host']})...")
    engine = create_engine(connection_string, connect_args=ssl_args)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.fetchone()
    print("   -> Connection OK")
    
    # Push data
    table_name = cfg["table"]
    print(f"   -> Pushing {len(df):,} rows to table '{table_name}'...")
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"   -> Done! Data is now live on TiDB Cloud")
    
    engine.dispose()


def main():
    """Run all crawlers in parallel and process results."""
    start_time = time.time()
    
    # 1. Run all crawlers in parallel
    df_all = run_all_crawlers()
    
    if df_all.empty:
        print(" No data collected.")
        return

    # 2. Add synthetic features (Vectorized operation)
    print("\n" + "=" * 50)
    print(" ADDING SYNTHETIC FEATURES")
    print("=" * 50)
    df_all = add_synthetic_customer_features(df_all)

    # 3. Filter and Reorder columns
    print(f"   -> Filtering columns...")
    available_cols = [c for c in FINAL_COLUMNS if c in df_all.columns]
    df_all = df_all[available_cols]

    # Strip timezone info from dates (real crawled dates are tz-aware,
    # but Excel/openpyxl requires tz-naive datetimes)
    if 'date' in df_all.columns:
        df_all['date'] = pd.to_datetime(df_all['date'], errors='coerce')
        df_all['date'] = df_all['date'].dt.tz_localize(None)

    # 4. Save locally (CSV + Excel)
    output_path_csv = Path(__file__).parent / "data" / "processed" / "merged_all_reviews.csv"
    output_path_excel = Path(__file__).parent / "data" / "processed" / "merged_all_reviews.xlsx"
    
    output_path_csv.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 50)
    print(" SAVING DATA (Local)")
    print("=" * 50)
    
    # Save CSV
    try:
        print(f"   -> Saving to CSV: {output_path_csv.name}")
        df_all.to_csv(output_path_csv, index=False, encoding="utf-8-sig")
    except PermissionError:
        output_path_csv = output_path_csv.with_name(f"merged_all_reviews_{int(time.time())}.csv")
        print(f"   File locked! Saving to: {output_path_csv.name}")
        df_all.to_csv(output_path_csv, index=False, encoding="utf-8-sig")

    # Save Excel
    try:
        print(f"   -> Saving to Excel: {output_path_excel.name}")
        df_all.to_excel(output_path_excel, index=False, engine='openpyxl')
    except PermissionError:
        output_path_excel = output_path_excel.with_name(f"merged_all_reviews_{int(time.time())}.xlsx")
        print(f"   File locked! Saving to: {output_path_excel.name}")
        df_all.to_excel(output_path_excel, index=False, engine='openpyxl')

    # 5. Push to TiDB Cloud
    print("\n" + "=" * 50)
    print(" PUSHING TO TIDB CLOUD")
    print("=" * 50)
    try:
        push_to_tidb(df_all)
    except Exception as e:
        print(f"   Failed to push to TiDB: {e}")
        print("   (Local files were saved successfully)")

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(" DATA COLLECTION COMPLETE")
    print("=" * 60)
    print(f"\n Summary:")
    print(f"   Total rows: {len(df_all):,}")
    print(f"   Banks: {df_all['bank_name'].nunique()}")
    print(f"   Platforms: {df_all['platform'].nunique()}")
    print(f"   Churn rate: {df_all['churn'].mean():.2%}")
    print(f"   Time taken: {elapsed:.2f} seconds")
    print(f"\n Local CSV: {output_path_csv}")
    print(f" Local Excel: {output_path_excel}")
    print(f" TiDB Cloud: {TIDB_CONFIG['database']}.{TIDB_CONFIG['table']}")
    print("=" * 60 + "\n")

    return df_all


if __name__ == "__main__":
    main()

