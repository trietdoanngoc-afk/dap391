"""
Apple App Store Real Review Scraper.

Uses Apple's public iTunes RSS/JSON API to fetch actual user reviews
for Vietnamese bank apps. No third-party library needed.

API endpoint:
    https://itunes.apple.com/vn/rss/customerreviews/id={APP_ID}/sortBy=mostRecent/page={PAGE}/json
"""

import random
import requests
import pandas as pd

from config import BANK_APPS_IOS


def _fetch_reviews_for_app(app_id: int, max_pages: int = 4) -> list:
    """
    Fetch reviews from Apple's public RSS JSON feed.
    Each page returns up to 50 reviews. Max 10 pages available.
    """
    all_reviews = []

    for page in range(1, max_pages + 1):
        url = (
            f"https://itunes.apple.com/vn/rss/customerreviews/"
            f"id={app_id}/sortBy=mostRecent/page={page}/json"
        )
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                break

            for entry in entries:
                # Skip the first entry if it's the app metadata (not a review)
                if "im:rating" not in entry:
                    continue

                all_reviews.append({
                    "rating": int(entry["im:rating"]["label"]),
                    "title": entry.get("title", {}).get("label", ""),
                    "content": entry.get("content", {}).get("label", ""),
                    "author": entry.get("author", {}).get("name", {}).get("label", ""),
                    "date": entry.get("updated", {}).get("label", None),
                })
        except Exception:
            break

    return all_reviews


def crawl_apple_store(count_per_bank: int = 200) -> pd.DataFrame:
    """
    Crawl real reviews from Apple App Store for all configured banks.

    Args:
        count_per_bank: Target number of reviews per bank (max ~500 via RSS).

    Returns:
        DataFrame with columns: review_id, date, bank_name, rating, churn,
        platform, data_source, content
    """
    all_rows = []
    max_pages = min(max(count_per_bank // 50, 1), 10)

    for bank_name, app_id in BANK_APPS_IOS.items():
        if app_id is None:
            print(f"      Skip {bank_name} (no App Store ID)")
            continue

        try:
            reviews = _fetch_reviews_for_app(app_id, max_pages=max_pages)

            for i, r in enumerate(reviews):
                rating = r["rating"]
                all_rows.append({
                    "review_id": str(random.randint(10_000_000_000, 99_999_999_999)),
                    "date": r.get("date", None),
                    "bank_name": bank_name,
                    "rating": rating,
                    "churn": 1 if rating <= 2 else 0,
                    "platform": "app_store",
                    "data_source": "real_crawl",
                    "content": str(r.get("content", "")).strip(),
                })

            print(f"      {bank_name}: {len(reviews)} reviews (App Store)")

        except Exception as e:
            print(f"      {bank_name} (App Store): {e}")

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    print(f"   App Store total: {len(df):,} real reviews")
    return df
