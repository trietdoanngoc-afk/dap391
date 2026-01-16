"""
Facebook Review Generator.
Generates synthetic Facebook review data for banks.
"""

import sys
from pathlib import Path

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BANKS_ALL
from utils import add_synthetic_customer_features, generate_dummy_reviews


def crawl_facebook() -> pd.DataFrame:
    """
    Generate synthetic Facebook review data for all banks.
    
    Note: Facebook does not provide a public API for page reviews,
    so this generates synthetic data for demonstration purposes.
    
    Returns
    -------
    pandas.DataFrame
        Combined DataFrame with synthetic reviews from all banks
    """
    print("\n" + "=" * 50)
    print("📘 FACEBOOK REVIEW GENERATOR (Synthetic)")
    print("=" * 50 + "\n")

    all_dfs = []

    for bank_name in BANKS_ALL:
        print(f"→ Generating: {bank_name}")
        df_bank = generate_dummy_reviews(bank_name, "facebook", count=500)
        all_dfs.append(df_bank)

    df = pd.concat(all_dfs, ignore_index=True)
    df = add_synthetic_customer_features(df)

    return df


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    df = crawl_facebook()
    
    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "raw" / "reviews_facebook.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 50)
    print(f"✅ Saved: {output_path}")
    print(f"   Rows: {len(df):,}")
    print(f"   Banks: {df['bank_name'].nunique()}")
    print(f"   Churn rate: {df['churn'].mean():.2%}")
    print("=" * 50)
