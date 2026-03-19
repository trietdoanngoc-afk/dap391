"""
Preprocessing Pipeline for Bank Review Analysis.

5-Step Pipeline:
    1. Data Cleaning
    2. Categorical Encoding
    3. Outlier Handling
    4. Feature Engineering
    5. Feature Scaling

Each step is implemented as a class with fit_transform/transform methods.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler


# =============================================================================
# STEP 1: DATA CLEANING
# =============================================================================

class DataCleaner:
    """
    Buoc 1: Data Cleaning (Lam sach du lieu)

    Phuong phap:
    - Drop Duplicates: Xoa cac hang trung lap hoan toan
    - Handle Missing Values: Xu ly gia tri null (median cho so, mode cho chu)
    - Fix Data Types: Chuyen doi kieu du lieu dung (date str -> datetime)
    - Drop Irrelevant Columns: Xoa cot khong can thiet cho mo hinh (review_id, data_source)

    Vi sao:
    - Du lieu trung lap lam model bi bias (thien lech)
    - Gia tri null gay loi khi train model
    - Kieu du lieu sai se khong the tinh toan dung
    - Cot ID khong mang thong tin du doan, giu lai se gay noise
    """

    def __init__(self, drop_columns=None):
        self.drop_columns = drop_columns or ["review_id", "data_source"]
        self.stats = {}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()

        # --- 1a. Drop Duplicates ---
        before = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        self.stats["duplicates_removed"] = before - len(df_clean)
        print(f"   [1a] Drop Duplicates: Xoa {self.stats['duplicates_removed']} hang trung lap")

        # --- 1b. Handle Missing Values ---
        null_counts = df_clean.isnull().sum()
        total_nulls = null_counts.sum()
        if total_nulls > 0:
            # Numeric: fill with median
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df_clean[col].isnull().any():
                    median_val = df_clean[col].median()
                    df_clean[col].fillna(median_val, inplace=True)
                    print(f"       Fill '{col}' nulls with median = {median_val}")

            # Categorical: fill with mode
            cat_cols = df_clean.select_dtypes(include=["object", "string"]).columns
            for col in cat_cols:
                if df_clean[col].isnull().any():
                    mode_val = df_clean[col].mode()[0]
                    df_clean[col].fillna(mode_val, inplace=True)
                    print(f"       Fill '{col}' nulls with mode = {mode_val}")

        self.stats["nulls_handled"] = total_nulls
        print(f"   [1b] Handle Missing: {total_nulls} null values xu ly")

        # --- 1c. Fix Data Types ---
        if "date" in df_clean.columns:
            df_clean["date"] = pd.to_datetime(df_clean["date"], errors="coerce")
            print(f"   [1c] Fix Dtypes: 'date' str -> datetime")

        # --- 1d. Drop Irrelevant Columns ---
        cols_dropped = [c for c in self.drop_columns if c in df_clean.columns]
        df_clean = df_clean.drop(columns=cols_dropped, errors="ignore")
        print(f"   [1d] Drop Columns: {cols_dropped}")

        print(f"   Data Cleaning xong: {df_clean.shape}")
        return df_clean


# =============================================================================
# STEP 2: CATEGORICAL ENCODING
# =============================================================================

class CategoricalEncoder:
    """
    Buoc 2: Categorical Encoding (Ma hoa bien phan loai)

    Phuong phap:
    - Binary Encoding (sex): Male=1, Female=0
    - One-Hot Encoding (platform): Tao 3 cot dummy (app_store, google_play, facebook)
    - Label Encoding (bank_name): Gan moi bank 1 so nguyen (0-34)
    """

    def __init__(self):
        self.label_encoder_bank = LabelEncoder()
        self.binary_map = {"Male": 1, "Female": 0}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_encoded = df.copy()

        # --- 2a. Binary Encoding: sex ---
        if "sex" in df_encoded.columns:
            df_encoded["sex"] = df_encoded["sex"].map(self.binary_map)
            print(f"   [2a] Binary Encoding 'sex': Male->1, Female->0")

        # --- 2b. One-Hot Encoding: platform ---
        if "platform" in df_encoded.columns:
            dummies = pd.get_dummies(df_encoded["platform"], prefix="platform", dtype=int)
            df_encoded = pd.concat([df_encoded.drop("platform", axis=1), dummies], axis=1)
            print(f"   [2b] One-Hot Encoding 'platform': -> {list(dummies.columns)}")

        # --- 2c. Label Encoding: bank_name ---
        if "bank_name" in df_encoded.columns:
            df_encoded["bank_name"] = self.label_encoder_bank.fit_transform(
                df_encoded["bank_name"].astype(str)
            )
            n_classes = len(self.label_encoder_bank.classes_)
            print(f"   [2c] Label Encoding 'bank_name': {n_classes} banks -> 0..{n_classes-1}")

        print(f"   Categorical Encoding xong: {df_encoded.shape}")
        return df_encoded


# =============================================================================
# STEP 3: OUTLIER HANDLING
# =============================================================================

class OutlierHandler:
    """
    Buoc 3: Outlier Handling (Xu ly ngoai le)

    Phuong phap: IQR (Interquartile Range)
    - Q1 = percentile 25%, Q3 = percentile 75%
    - IQR = Q3 - Q1
    - Lower bound = Q1 - 1.5 * IQR
    - Upper bound = Q3 + 1.5 * IQR
    - Gia tri ngoai [lower, upper] duoc CAP (cat) ve bien gan nhat
    """

    def __init__(self, columns=None, factor=1.5):
        self.columns = columns or ["age", "credit_score", "balance", "tenure"]
        self.factor = factor
        self.bounds = {}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        total_capped = 0

        for col in self.columns:
            if col not in df_clean.columns:
                continue

            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - self.factor * IQR
            upper = Q3 + self.factor * IQR

            self.bounds[col] = {"Q1": Q1, "Q3": Q3, "IQR": IQR, "lower": lower, "upper": upper}

            # Count outliers
            n_outliers = ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
            total_capped += n_outliers

            # CAP outliers (thay vi xoa hang)
            df_clean[col] = df_clean[col].clip(lower=lower, upper=upper)

            print(f"   [3] IQR '{col}': Q1={Q1:.0f}, Q3={Q3:.0f}, IQR={IQR:.0f}")
            print(f"       Bounds=[{lower:.0f}, {upper:.0f}], Capped={n_outliers} values")

        print(f"   Outlier Handling xong: Tong {total_capped} gia tri da capped")
        return df_clean


# =============================================================================
# STEP 4: FEATURE ENGINEERING
# =============================================================================

class FeatureEngineer:
    """
    Buoc 4: Feature Engineering (Tao dac trung moi)

    Features tao moi:
    1. balance_per_product = balance / products_number
    2. tenure_age_ratio = tenure / age
    3. is_high_value = (balance > median) AND (credit_score > 600)
    4. review_month = Thang tu cot date
    5. review_day_of_week = Thu trong tuan tu cot date
    """

    def __init__(self):
        self.balance_median = None

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_feat = df.copy()

        # --- 4a. balance_per_product ---
        if "balance" in df_feat.columns and "products_number" in df_feat.columns:
            df_feat["balance_per_product"] = (
                df_feat["balance"] / df_feat["products_number"].replace(0, 1)
            )
            print(f"   [4a] balance_per_product = balance / products_number")

        # --- 4b. tenure_age_ratio ---
        if "tenure" in df_feat.columns and "age" in df_feat.columns:
            df_feat["tenure_age_ratio"] = df_feat["tenure"] / df_feat["age"].replace(0, 1)
            print(f"   [4b] tenure_age_ratio = tenure / age")

        # --- 4c. is_high_value ---
        if "balance" in df_feat.columns and "credit_score" in df_feat.columns:
            self.balance_median = df_feat["balance"].median()
            df_feat["is_high_value"] = (
                (df_feat["balance"] > self.balance_median) &
                (df_feat["credit_score"] > 600)
            ).astype(int)
            print(f"   [4c] is_high_value = (balance > {self.balance_median:.0f}) AND (credit_score > 600)")

        # --- 4d & 4e. Temporal features ---
        if "date" in df_feat.columns and pd.api.types.is_datetime64_any_dtype(df_feat["date"]):
            df_feat["review_month"] = df_feat["date"].dt.month
            df_feat["review_day_of_week"] = df_feat["date"].dt.dayofweek
            df_feat = df_feat.drop(columns=["date"])
            print(f"   [4d] review_month = month extracted from date")
            print(f"   [4e] review_day_of_week = dayofweek (0=Mon, 6=Sun)")
            print(f"       Dropped 'date' column (replaced by extracted features)")

        print(f"   Feature Engineering xong: {df_feat.shape} (+{df_feat.shape[1] - df.shape[1]} features moi)")
        return df_feat


# =============================================================================
# STEP 5: FEATURE SCALING
# =============================================================================

class FeatureScaler:
    """
    Buoc 5: Feature Scaling (Chuan hoa gia tri)

    Phuong phap: MinMaxScaler
    - Cong thuc: X_scaled = (X - X_min) / (X_max - X_min)
    - Ket qua: Tat ca gia tri nam trong khoang [0, 1]
    """

    def __init__(self, method="minmax"):
        self.method = method
        self.scaler = MinMaxScaler() if method == "minmax" else StandardScaler()
        self.columns_to_scale = [
            "age", "tenure", "credit_score", "balance", "products_number",
            "balance_per_product", "tenure_age_ratio",
            "review_month", "review_day_of_week", "rating"
        ]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_scaled = df.copy()

        # Only scale columns that exist
        cols = [c for c in self.columns_to_scale if c in df_scaled.columns]

        if cols:
            df_scaled[cols] = self.scaler.fit_transform(df_scaled[cols])
            print(f"   [5] MinMaxScaler applied on: {cols}")
            print(f"       All values now in range [0, 1]")

        print(f"   Feature Scaling xong: {df_scaled.shape}")
        return df_scaled


# =============================================================================
# FULL PIPELINE
# =============================================================================

def preprocess_full_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full 5-step preprocessing pipeline.

    Pipeline:
        Raw Data -> Clean -> Encode -> Handle Outliers -> Engineer Features -> Scale

    Returns preprocessed DataFrame ready for modeling.
    Target variable: 'churn' (untouched)
    """
    print("\n" + "=" * 60)
    print(" PREPROCESSING PIPELINE")
    print("=" * 60)

    # Step 1
    print("\n STEP 1: DATA CLEANING")
    print("-" * 40)
    cleaner = DataCleaner()
    df = cleaner.fit_transform(df)

    # Step 2
    print("\n STEP 2: CATEGORICAL ENCODING")
    print("-" * 40)
    encoder = CategoricalEncoder()
    df = encoder.fit_transform(df)

    # Step 3
    print("\n STEP 3: OUTLIER HANDLING (IQR)")
    print("-" * 40)
    outlier_handler = OutlierHandler(factor=1.5)
    df = outlier_handler.fit_transform(df)

    # Step 4
    print("\n STEP 4: FEATURE ENGINEERING")
    print("-" * 40)
    engineer = FeatureEngineer()
    df = engineer.fit_transform(df)

    # Step 5
    print("\n STEP 5: FEATURE SCALING (MinMax)")
    print("-" * 40)
    scaler = FeatureScaler(method="minmax")
    df = scaler.fit_transform(df)

    print("\n" + "=" * 60)
    print(f" PIPELINE COMPLETE: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("=" * 60)

    return df
