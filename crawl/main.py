"""
Main script to run all crawlers and merge the data.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import FINAL_COLUMNS
from crawlers import crawl_apple_store, crawl_google_play, crawl_facebook


def main():
    """Run all crawlers and merge results."""
    print("\n" + "=" * 60)
    print("🏦 BANK REVIEW DATA COLLECTION")
    print("=" * 60)

    # Collect data from all sources
    df_appstore = crawl_apple_store()
    df_googleplay = crawl_google_play()
    df_facebook = crawl_facebook()

    # Merge all data
    print("\n" + "=" * 50)
    print("🔗 MERGING ALL DATA")
    print("=" * 50)

    df_all = pd.concat(
        [df_appstore, df_googleplay, df_facebook], 
        ignore_index=True
    )

    # Reorder columns (only include columns that exist)
    available_cols = [c for c in FINAL_COLUMNS if c in df_all.columns]
    df_all = df_all[available_cols]

    # Save merged data
    output_path = Path(__file__).parent / "data" / "processed" / "merged_all_reviews.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(output_path, index=False, encoding="utf-8-sig")

    # Summary
    print("\n" + "=" * 60)
    print("✅ DATA COLLECTION COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Total rows: {len(df_all):,}")
    print(f"   • Banks: {df_all['bank_name'].nunique()}")
    print(f"   • Platforms: {df_all['platform'].nunique()}")
    print(f"   • Churn rate: {df_all['churn'].mean():.2%}")
    print(f"\n📁 Output: {output_path}")
    print("=" * 60 + "\n")

    return df_all


if __name__ == "__main__":
    main()
