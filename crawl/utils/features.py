"""
Feature generation utilities.
Contains functions to add synthetic customer features to review data.
"""

import random


def add_synthetic_customer_features(df, seed=42):
    """
    Add synthetic customer features to a DataFrame.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing review data
    seed : int, optional
        Random seed for reproducibility (default: 42)
    
    Returns
    -------
    pandas.DataFrame
        DataFrame with added customer features
    
    Features Added
    --------------
    - sex: Male/Female (48%/52% split)
    - age: 18-70 years
    - tenure: 0 to min(20, age-18) years
    - credit_score: 300-850
    - balance: 0 to 2 billion VND
    - products_number: 1-5 products
    - credit_card: 0/1 (40%/60% split)
    - active_member: 0/1 (30%/70% split)
    """
    random.seed(seed)
    n = len(df)

    # Demographics
    df["sex"] = random.choices(
        ["Male", "Female"], 
        weights=[48, 52], 
        k=n
    )
    df["age"] = [random.randint(18, 70) for _ in range(n)]
    df["tenure"] = [
        random.randint(0, min(20, age - 18)) 
        for age in df["age"]
    ]

    # Financial indicators
    df["credit_score"] = [random.randint(300, 850) for _ in range(n)]
    df["balance"] = [
        round(random.uniform(0, 2_000_000_000), 0) 
        for _ in range(n)
    ]
    df["products_number"] = random.choices(
        [1, 2, 3, 4, 5], 
        weights=[30, 30, 20, 15, 5], 
        k=n
    )

    # Account status
    df["credit_card"] = random.choices([0, 1], weights=[40, 60], k=n)
    df["active_member"] = random.choices([0, 1], weights=[30, 70], k=n)

    return df
