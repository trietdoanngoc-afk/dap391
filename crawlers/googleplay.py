"""
Google Play Store Real Review Scraper.

Uses google-play-scraper library to fetch actual user reviews
for Vietnamese bank apps from the Google Play Store.
"""

import random
import pandas as pd
from google_play_scraper import reviews, Sort

from config import BANK_APPS_GOOGLE


def crawl_google_play(count_per_bank: int = 200) -> pd.DataFrame:
    """
    Crawl real reviews from Google Play Store for all configured banks.

    Args:
        count_per_bank: Number of reviews to fetch per bank app.

    Returns:
        DataFrame with columns: review_id, date, bank_name, rating, churn,
        platform, data_source, content
    """
    all_rows = []

    for bank_name, package_id in BANK_APPS_GOOGLE.items():
        if not package_id:
            print(f"      Skip {bank_name} (no Google Play package ID)")
            continue

        try:
            result, _ = reviews(
                package_id,
                lang='vi',
                country='vn',
                sort=Sort.NEWEST,
                count=count_per_bank,
            )

            for i, r in enumerate(result):
                rating = int(r.get('score', 3))
                all_rows.append({
                    'review_id': str(random.randint(10_000_000_000, 99_999_999_999)),
                    'date': r.get('at', None),
                    'bank_name': bank_name,
                    'rating': rating,
                    'churn': 1 if rating <= 2 else 0,
                    'platform': 'google_play',
                    'data_source': 'real_crawl',
                    'content': str(r.get('content', '')).strip(),
                })

            print(f"      {bank_name}: {len(result)} reviews (Google Play)")

        except Exception as e:
            print(f"      {bank_name} (Google Play): {e}")

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    print(f"   Google Play total: {len(df):,} real reviews")
    return df
