import pandas as pd
import random
from datetime import datetime, timedelta

# =====================================================
# 1️⃣ FACEBOOK DUMMY GENERATOR (GIỐNG APP STORE)
# =====================================================
def generate_facebook_dummy(bank_name, how_many=500):
    data = []
    start_date = datetime.now() - timedelta(days=30)

    for i in range(how_many):
        rating = random.choices(
            [1, 2, 3, 4, 5],
            weights=[12, 13, 25, 25, 25]
        )[0]

        churn = 1 if rating <= 2 else 0

        data.append({
            "review_id": f"FB_{bank_name[:3].upper()}_{i:04d}",
            "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "bank_name": bank_name,
            "rating": rating,
            "churn": churn,
            "platform": "facebook",
            "data_source": "synthetic"
        })

    return pd.DataFrame(data)

# =====================================================
# 2️⃣ SYNTHETIC CUSTOMER FEATURES (DÙNG CHUNG)
# =====================================================
def add_synthetic_customer_features(df):
    random.seed(42)
    n = len(df)

    df["country_of_residence"] = "Vietnam"

    df["sex"] = random.choices(
        ["Male", "Female"],
        weights=[0.48, 0.52],
        k=n
    )

    df["age"] = [random.randint(18, 70) for _ in range(n)]

    df["tenure"] = [
        random.randint(0, min(20, age - 18))
        for age in df["age"]
    ]

    df["credit_score"] = [
        random.randint(300, 850) for _ in range(n)
    ]

    df["balance"] = [
        round(random.uniform(0, 2_000_000_000), 0)
        for _ in range(n)
    ]

    df["products_number"] = random.choices(
        [1, 2, 3, 4, 5],
        weights=[30, 30, 20, 15, 5],
        k=n
    )

    df["credit_card"] = random.choices(
        [0, 1],
        weights=[40, 60],
        k=n
    )

    df["active_member"] = random.choices(
        [0, 1],
        weights=[30, 70],
        k=n
    )

    return df

# =====================================================
# 3️⃣ GENERATE FACEBOOK DATA CHO NHIỀU BANK
# =====================================================
BANKS_FACEBOOK = [
    "Vietcombank",
    "BIDV",
    "VietinBank",
    "Agribank",

    # 🔵 Private banks
    "Techcombank",
    "MB Bank",
    "TPBank",
    "VPBank",
    "SHB",
    "HDBank",
    "OCB",
    "ACB",
    "Sacombank",
    "Eximbank",
    "SeABank",
    "Bac A Bank",
    "LienVietPostBank",
    "Nam A Bank",
    "PVcomBank",
    "Kienlongbank",
    "ABBank",
    "NCB",
    # 🟣 Foreign banks
    "HSBC Vietnam",
    "Standard Chartered VN",
    "Shinhan Bank VN",
    "UOB VN",
    "OCBC VN",
    "Public Bank VN",
    "Hong Leong VN",
    "Indovina Bank",
    "Maybank VN",

    # 🟠 Others
    "VietABank",
    "Saigonbank",
    "VRB",
    "PG Bank"
]

all_fb_dfs = []

for bank in BANKS_FACEBOOK:
    df_fb_bank = generate_facebook_dummy(bank, how_many=500)
    all_fb_dfs.append(df_fb_bank)

df_fb = pd.concat(all_fb_dfs, ignore_index=True)

# 👉 ADD CUSTOMER FEATURES
df_fb = add_synthetic_customer_features(df_fb)

# =====================================================
# 4️⃣ SAVE + STATS
# =====================================================
df_fb.to_csv(
    "bank_reviews_facebook.csv",
    index=False,
    encoding="utf-8-sig"
)

print("✅ Saved bank_reviews_facebook.csv")
print("Rows:", len(df_fb))
print("Banks covered:", df_fb["bank_name"].nunique())
print("Churn rate:", f"{df_fb['churn'].mean():.2%}")
