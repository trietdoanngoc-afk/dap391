"""
Apple App Store Review Crawler.
Generates synthetic review data for demonstration.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BANKS_ALL
from utils import add_synthetic_customer_features, generate_dummy_reviews


def crawl_apple_store() -> pd.DataFrame:
    """
    Generate synthetic Apple App Store reviews for all banks.
    
    Returns
    -------
    pandas.DataFrame
        Combined DataFrame with reviews from all banks
    """
    print("\n" + "=" * 50)
    print("📱 APPLE APP STORE DATA")
    print("=" * 50 + "\n")

    all_dfs = []

    for bank_name in BANKS_ALL:
        print(f"→ Generating: {bank_name}")
        df_bank = generate_dummy_reviews(bank_name, "app_store", count=300)
        all_dfs.append(df_bank)

    df = pd.concat(all_dfs, ignore_index=True)
    df = add_synthetic_customer_features(df)

    return df


if __name__ == "__main__":
    df = crawl_apple_store()
    
    output_path = Path(__file__).parent.parent / "data" / "raw" / "reviews_appstore.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\n✅ Saved: {output_path}")
    print(f"   Rows: {len(df):,}")
