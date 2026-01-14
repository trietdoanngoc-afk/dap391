import pandas as pd
import requests
from datetime import datetime, timedelta
import random

# =====================================================
# 1️⃣ DANH SÁCH NGÂN HÀNG + APP ID IOS
# None = không có RSS → dùng dummy
# =====================================================
BANK_APPS_IOS = {
    # 🟡 Big 4
    "Vietcombank": 561433133,
    "BIDV": 1061867449,
    "VietinBank": 689963454,
    "Agribank": 935944952,

    # 🔵 Private banks
    "Techcombank": 1548623362,
    "MB Bank": 1205807363,
    "TPBank": 450464147,
    "VPBank": 1209349510,
    "SHB": 1661457183,
    "HDBank": 1461658565,
    "OCB": 6472261202,
    "ACB": 950141024,
    "Sacombank": 1436283663,
    "Eximbank": 1571427361,
    "SeABank": 846407152,
    "Bac A Bank": 1441408786,
    "LienVietPostBank": 1488794748,
    "Nam A Bank": 1456997296,
    "PVcomBank": 6467857410,
    "Kienlongbank": 1562823941,
    "ABBank": 6636532294,
    "NCB": 1435405040,

    # 🟣 Foreign banks
    "HSBC Vietnam": 1472163155,
    "Standard Chartered VN": None,
    "Shinhan Bank VN": 1071033810,
    "UOB VN": 1174327324,
    "OCBC VN": None,
    "Public Bank VN": 1573736472,
    "Hong Leong VN": None,
    "Indovina Bank": 1096963960,
    "Maybank VN": None,

    # 🟠 Others
    "VietABank": 6744814738,
    "Saigonbank": 1481832587,
    "VRB": None,
    "PG Bank": 1537765475
}

# =====================================================
# 2️⃣ HÀM CRAWL APPLE RSS (SAFE + DUMMY FALLBACK)
# =====================================================
def crawl_apple_rss_safe(app_id, bank_name, pages=10):
    data = []

    # --- Try RSS ---
    if app_id:
        for page in range(1, pages + 1):
            url = f"https://itunes.apple.com/vn/rss/customerreviews/id={app_id}/page={page}/sortby=mostrecent/json"
            try:
                r = requests.get(url, timeout=10)
                if r.status_code != 200:
                    break

                entries = r.json().get("feed", {}).get("entry", [])
                if not isinstance(entries, list):
                    continue

                for e in entries:
                    if "im:rating" not in e:
                        continue

                    rating = int(e["im:rating"]["label"])
                    churn = 1 if rating <= 1 else 0

                    data.append({
                        "review_id": e["id"]["label"].split("/")[-1],
                        "date": e["updated"]["label"][:10],
                        "bank_name": bank_name,
                        "rating": rating,
                        "churn": churn,
                        "platform": "app_store"
                    })
            except Exception:
                break

    # --- Dummy fallback ---
    if len(data) == 0:
        print(f"⚠️ Apple RSS empty for {bank_name} → using dummy data")
        start_date = datetime.now() - timedelta(days=30)

        for i in range(300):
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[10, 15, 25, 25, 25]
            )[0]

            churn = 1 if rating <= 2 else 0

            data.append({
                "review_id": f"{bank_name[:3].upper()}_DUMMY_{i}",
                "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "bank_name": bank_name,
                "rating": rating,
                "churn": churn,
                "platform": "app_store_dummy"
            })

    return pd.DataFrame(data)

# =====================================================
# 3️⃣ SYNTHETIC CUSTOMER FEATURES
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
# 4️⃣ CHẠY CRAWL TOÀN BỘ NGÂN HÀNG
# =====================================================
print("\n=== STARTING APPLE STORE CRAWL ===\n")

all_dfs = []

for bank_name, app_id in BANK_APPS_IOS.items():
    print(f"→ Processing {bank_name}")
    df_bank = crawl_apple_rss_safe(app_id, bank_name)
    all_dfs.append(df_bank)

df_ios = pd.concat(all_dfs, ignore_index=True)

# 👉 ADD SYNTHETIC CUSTOMER FEATURES
df_ios = add_synthetic_customer_features(df_ios)

# =====================================================
# 5️⃣ LƯU FILE + THỐNG KÊ
# =====================================================
df_ios.to_csv(
    "bank_app_reviews_apple_store.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n✅ Saved bank_app_reviews_apple_store.csv")
print("Total rows:", len(df_ios))
print("Banks covered:", df_ios["bank_name"].nunique())
print("Churn rate:", f"{df_ios['churn'].mean():.2%}")
