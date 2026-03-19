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
    
    start_date = datetime.now() - timedelta(days=days_back)
    
    # Bulk generate random values
    ratings = random.choices([1, 2, 3, 4, 5], weights=rating_weights, k=count)
    days_offsets = [random.randint(0, days_back) for _ in range(count)]
    
    # Generate 11-digit IDs
    # Using string formatting for speed and ensuring 11 digits (leading zeros if any, though range starts at 10B)
    ids = [str(random.randint(10_000_000_000, 99_999_999_999)) for _ in range(count)]
    
    # Pre-calculate date strings
    dates = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d") for d in days_offsets]
    
    data = {
        "review_id": ids,
        "date": dates,
        "bank_name": [bank_name] * count,
        "rating": ratings,
        "churn": [1 if r <= 2 else 0 for r in ratings],
        "platform": [platform] * count,
        "data_source": ["synthetic"] * count
    }

    return pd.DataFrame(data)
