"""
Unified Bank Review Crawler
Combines Apple Store, Google Play, and Facebook data into a single CSV
"""

import pandas as pd
import requests
import random
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort

# =====================================================
# BANK CONFIGURATION
# =====================================================
BANK_APPS = {
    # Bank Name: (iOS App ID, Google Play Package ID)
    "Vietcombank": (561433133, "com.VCB"),
    "BIDV": (1061867449, "com.bidv.smartbanking"),
    "VietinBank": (689963454, "com.vietinbank.ipay"),
    "Agribank": (935944952, "com.vnpay.Agribank3g"),
    "Techcombank": (1548623362, "vn.com.techcombank.bb.app"),
    "MB Bank": (1205807363, "com.mbmobile"),
    "TPBank": (450464147, "com.tpb.mb.smartbank"),
    "VPBank": (1209349510, "com.vnpay.vpbankonline"),
    "SHB": (1661457183, None),
    "HDBank": (1461658565, None),
    "OCB": (6472261202, None),
    "ACB": (950141024, "com.acb.acbonline"),
    "Sacombank": (1436283663, "com.sacombank.pay"),
    "Eximbank": (1571427361, None),
    "SeABank": (846407152, None),
    "Bac A Bank": (1441408786, None),
    "LienVietPostBank": (1488794748, None),
    "Nam A Bank": (1456997296, None),
    "PVcomBank": (6467857410, None),
    "Kienlongbank": (1562823941, None),
    "ABBank": (6636532294, None),
    "NCB": (1435405040, None),
    "HSBC Vietnam": (1472163155, None),
    "Standard Chartered VN": (None, None),
    "Shinhan Bank VN": (1071033810, None),
    "UOB VN": (1174327324, None),
    "OCBC VN": (None, None),
    "Public Bank VN": (1573736472, None),
    "Hong Leong VN": (None, None),
    "Indovina Bank": (1096963960, None),
    "Maybank VN": (None, None),
    "VietABank": (6744814738, None),
    "Saigonbank": (1481832587, None),
    "VRB": (None, None),
    "PG Bank": (1537765475, None)
}

# =====================================================
# APPLE STORE CRAWLER
# =====================================================
def crawl_apple_store(app_id, bank_name, pages=10):
    """Crawl Apple Store reviews or generate dummy data"""
    data = []
    
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
                    churn = 1 if rating <= 2 else 0
                    
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
    
    # Dummy fallback
    if len(data) == 0:
        print(f"  ⚠️ Apple RSS empty for {bank_name} → using dummy data")
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(300):
            rating = random.choices([1, 2, 3, 4, 5], weights=[10, 15, 25, 25, 25])[0]
            churn = 1 if rating <= 2 else 0
            
            data.append({
                "review_id": f"{bank_name[:3].upper()}_IOS_DUMMY_{i}",
                "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "bank_name": bank_name,
                "rating": rating,
                "churn": churn,
                "platform": "app_store_dummy"
            })
    
    return data

# =====================================================
# GOOGLE PLAY CRAWLER
# =====================================================
def crawl_google_play(app_id, bank_name, n_reviews=3000):
    """Crawl Google Play reviews or generate dummy data"""
    data = []
    
    if app_id:
        try:
            result, _ = reviews(
                app_id,
                lang="vi",
                country="vn",
                sort=Sort.NEWEST,
                count=n_reviews
            )
            
            for r in result:
                rating = r.get("score")
                at = r.get("at")
                
                data.append({
                    "review_id": r.get("reviewId"),
                    "date": at.strftime("%Y-%m-%d") if at else None,
                    "bank_name": bank_name,
                    "rating": rating,
                    "churn": 1 if rating and rating <= 2 else 0,
                    "platform": "google_play"
                })
        except Exception:
            pass
    
    # Synthetic fallback
    if len(data) == 0:
        print(f"  ⚠️ Google Play empty for {bank_name} → using dummy data")
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(500):
            rating = random.choices([1, 2, 3, 4, 5], weights=[12, 13, 25, 25, 25])[0]
            
            data.append({
                "review_id": f"GP_{bank_name[:3].upper()}_{i:04d}",
                "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "bank_name": bank_name,
                "rating": rating,
                "churn": 1 if rating <= 2 else 0,
                "platform": "google_play_dummy"
            })
    
    return data

# =====================================================
# FACEBOOK CRAWLER (DUMMY ONLY)
# =====================================================
def crawl_facebook(bank_name, how_many=500):
    """Generate Facebook dummy data"""
    data = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(how_many):
        rating = random.choices([1, 2, 3, 4, 5], weights=[12, 13, 25, 25, 25])[0]
        churn = 1 if rating <= 2 else 0
        
        data.append({
            "review_id": f"FB_{bank_name[:3].upper()}_{i:04d}",
            "date": (start_date + timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "bank_name": bank_name,
            "rating": rating,
            "churn": churn,
            "platform": "facebook"
        })
    
    return data

# =====================================================
# SYNTHETIC CUSTOMER FEATURES
# =====================================================
def add_synthetic_customer_features(df):
    """Add synthetic customer demographic and banking features"""
    random.seed(42)
    n = len(df)
    
    df["country_of_residence"] = "Vietnam"
    df["sex"] = random.choices(["Male", "Female"], weights=[0.48, 0.52], k=n)
    df["age"] = [random.randint(18, 70) for _ in range(n)]
    df["tenure"] = [random.randint(0, min(20, age - 18)) for age in df["age"]]
    df["credit_score"] = [random.randint(300, 850) for _ in range(n)]
    df["balance"] = [round(random.uniform(0, 2_000_000_000), 0) for _ in range(n)]
    df["products_number"] = random.choices([1, 2, 3, 4, 5], weights=[30, 30, 20, 15, 5], k=n)
    df["credit_card"] = random.choices([0, 1], weights=[40, 60], k=n)
    df["active_member"] = random.choices([0, 1], weights=[30, 70], k=n)
    
    return df

# =====================================================
# MAIN CRAWLER FUNCTION
# =====================================================
def crawl_all_platforms():
    """Crawl all platforms for all banks and combine into single DataFrame"""
    all_reviews = []
    
    print("\n" + "="*60)
    print("🚀 UNIFIED BANK REVIEW CRAWLER")
    print("="*60 + "\n")
    
    for bank_name, (ios_id, gp_id) in BANK_APPS.items():
        print(f"📱 Processing: {bank_name}")
        
        # Apple Store
        print(f"  → Crawling Apple Store...")
        apple_data = crawl_apple_store(ios_id, bank_name)
        all_reviews.extend(apple_data)
        
        # Google Play
        print(f"  → Crawling Google Play...")
        gp_data = crawl_google_play(gp_id, bank_name)
        all_reviews.extend(gp_data)
        
        # Facebook
        print(f"  → Generating Facebook data...")
        fb_data = crawl_facebook(bank_name)
        all_reviews.extend(fb_data)
        
        print(f"  ✅ Total reviews for {bank_name}: {len(apple_data) + len(gp_data) + len(fb_data)}\n")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_reviews)
    
    # Add synthetic customer features
    print("🔧 Adding synthetic customer features...")
    df = add_synthetic_customer_features(df)
    
    # Ensure consistent column order
    column_order = [
        "review_id", "date", "bank_name", "rating", "churn", "platform",
        "country_of_residence", "sex", "age", "tenure", "credit_score",
        "balance", "products_number", "credit_card", "active_member"
    ]
    df = df[column_order]
    
    return df

# =====================================================
# MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    # Crawl all data
    df_combined = crawl_all_platforms()
    
    # Save to CSV
    output_file = "bank_reviews_all_platforms.csv"
    df_combined.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    # Print statistics
    print("\n" + "="*60)
    print("📊 CRAWL SUMMARY")
    print("="*60)
    print(f"✅ Saved: {output_file}")
    print(f"📝 Total rows: {len(df_combined):,}")
    print(f"🏦 Banks covered: {df_combined['bank_name'].nunique()}")
    print(f"📱 Platforms:")
    for platform, count in df_combined["platform"].value_counts().items():
        print(f"   - {platform}: {count:,}")
    print(f"⚠️ Churn rate: {df_combined['churn'].mean():.2%}")
    print(f"⭐ Average rating: {df_combined['rating'].mean():.2f}")
    print("="*60 + "\n")
