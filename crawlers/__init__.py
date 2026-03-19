"""
Crawlers package for collecting bank review data from various platforms.

Combines:
- Real crawlers for Google Play and Apple App Store
- Synthetic data generator for Facebook (no public API available)
"""

import concurrent.futures
import pandas as pd

from config import BANKS_ALL
from utils.generators import generate_dummy_reviews
from crawlers.googleplay import crawl_google_play
from crawlers.applestore import crawl_apple_store


def crawl_facebook_dummy(count: int = 500) -> pd.DataFrame:
    """
    Generate synthetic Facebook reviews.
    Facebook does not provide a public API for page reviews,
    so we continue using synthetic data for this platform.
    """
    print("   Generating synthetic Facebook reviews...")
    all_dfs = []
    for bank_name in BANKS_ALL:
        df_bank = generate_dummy_reviews(bank_name, "facebook", count=count)
        all_dfs.append(df_bank)
    return pd.concat(all_dfs, ignore_index=True)


def run_all_crawlers() -> pd.DataFrame:
    """
    Run all crawlers in parallel:
    - Google Play: REAL reviews
    - App Store: REAL reviews
    - Facebook: Synthetic (dummy) reviews
    """
    print("\n" + "=" * 50)
    print(" STARTING PARALLEL DATA COLLECTION")
    print("=" * 50)
    print("   Google Play & App Store -> REAL CRAWL")
    print("   Facebook -> Synthetic (no public API)")
    print()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(crawl_google_play, 200): "google_play",
            executor.submit(crawl_apple_store, 200): "app_store",
            executor.submit(crawl_facebook_dummy, 500): "facebook",
        }

        for future in concurrent.futures.as_completed(futures):
            platform = futures[future]
            try:
                df = future.result()
                if not df.empty:
                    results.append(df)
                    real_tag = "REAL" if platform != "facebook" else "SYNTHETIC"
                    print(f"   Completed: {platform} ({len(df):,} rows) [{real_tag}]")
                else:
                    print(f"   No data: {platform}")
            except Exception as exc:
                print(f"   Error collecting {platform}: {exc}")

    if not results:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)
