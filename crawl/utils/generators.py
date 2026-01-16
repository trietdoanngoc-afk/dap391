"""
Data generation utilities.
Contains functions to generate synthetic/dummy review data.
"""

import random
from datetime import datetime, timedelta

import pandas as pd


def generate_dummy_reviews(
    bank_name: str,
    platform: str,
    count: int = 500,
    rating_weights: list = None,
    days_back: int = 30
) -> pd.DataFrame:
    """
    Generate dummy review data for a bank.
    
    Parameters
    ----------
    bank_name : str
        Name of the bank
    platform : str
        Platform name (e.g., 'facebook', 'app_store', 'google_play')
    count : int, optional
        Number of reviews to generate (default: 500)
    rating_weights : list, optional
        Weights for ratings 1-5 (default: [12, 13, 25, 25, 25])
    days_back : int, optional
        Number of days in the past to generate dates for (default: 30)
    
    Returns
    -------
    pandas.DataFrame
        DataFrame with columns: review_id, date, bank_name, rating, churn, platform, data_source
    """
    if rating_weights is None:
        rating_weights = [12, 13, 25, 25, 25]
    
    data = []
    start_date = datetime.now() - timedelta(days=days_back)
    prefix = platform[:2].upper()
    bank_code = bank_name[:3].upper()

    for i in range(count):
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        churn = 1 if rating <= 2 else 0

        data.append({
            "review_id": f"{prefix}_{bank_code}_{i:04d}",
            "date": (start_date + timedelta(days=random.randint(0, days_back))).strftime("%Y-%m-%d"),
            "bank_name": bank_name,
            "rating": rating,
            "churn": churn,
            "platform": platform,
            "data_source": "synthetic"
        })

    return pd.DataFrame(data)
