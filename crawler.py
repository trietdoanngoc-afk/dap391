import pandas as pd
from google_play_scraper import Sort, reviews as google_reviews
from app_store_scraper import AppStore
from sqlalchemy import create_engine
import os
from datetime import datetime

# Import cấu hình các ngân hàng
from config import BANK_APPS_GOOGLE, BANK_APPS_IOS

print(f"[{datetime.now()}] BẮT ĐẦU CÀO DỮ LIỆU ĐỊNH KỲ TỪ CÁC CHỢ ỨNG DỤNG...")

all_reviews = []
# Số lượng review lấy mỗi tuần cho mỗi ngân hàng/mỗi nền tảng
REVIEWS_PER_BANK = 100 

# ==========================================
# 1. Cào dữ liệu từ GOOGLE PLAY (Android)
# ==========================================
print("\n--- ĐANG CÀO GOOGLE PLAY ---")
for bank, app_id in BANK_APPS_GOOGLE.items():
    if not app_id: continue
    print(f" Đang lấy review {bank} (Google Play)...")
    try:
        result, _ = google_reviews(
            app_id, 
            lang='vi', 
            country='vn', 
            sort=Sort.NEWEST, 
            count=REVIEWS_PER_BANK
        )
        for r in result:
            all_reviews.append({
                'reviewId': r['reviewId'],
                'userName': r['userName'],
                'content': r['content'],
                'rating': r['score'],
                'date': r['at'],
                'bank_name': bank,
                'data_source': 'google_play'
            })
    except Exception as e:
        print(f"   Lỗi {bank} (Google Play): {e}")


# ==========================================
# 2. Cào dữ liệu từ APP STORE (iOS)
# ==========================================
print("\n--- ĐANG CÀO APP STORE ---")
for bank, app_id in BANK_APPS_IOS.items():
    if not app_id: continue
    print(f" Đang lấy review {bank} (App Store)...")
    try:
        app = AppStore(country='vn', app_name=bank.lower().replace(" ", "-"), app_id=app_id)
        app.review(how_many=REVIEWS_PER_BANK)
        for r in app.reviews:
            all_reviews.append({
                'reviewId': str(r.get('id', '')),  # App Store có thể k có string ID rõ ràng
                'userName': r.get('userName', 'Unknown'),
                'content': r.get('review', ''),
                'rating': r.get('rating', 0),
                'date': r.get('date'),
                'bank_name': bank,
                'data_source': 'app_store'
            })
    except Exception as e:
        print(f"   Lỗi {bank} (App Store): {e}")

# ==========================================
# 3. Tiền xử lý (Data Processing / Deduplication)
# ==========================================
if not all_reviews:
    print("\nKhông cào được dòng dữ liệu nào! Thoát.")
    exit(0)

df = pd.DataFrame(all_reviews)

# Đảm bảo các cột có mặt
if 'reviewId' not in df.columns or df.empty:
    print("\nLỗi dữ liệu trống hoặc thiếu reviewId. Thoát.")
    exit(0)

print(f"\nTổng cộng cào được: {len(df)} reviews chưa lọc mộc.")

# LỌC TRÙNG (Deduplicate)
df = df.dropna(subset=['reviewId'])
df = df.drop_duplicates(subset=['reviewId'], keep='last')

# Tính toán nhãn Churn (<= 2 sao thì coi như Churned)
df['churn'] = df['rating'].apply(lambda x: 1 if x <= 2 else 0)

print(f"Sau khi LỌC TRÙNG (Deduplication) theo reviewId còn: {len(df)} reviews mới chuẩn bị đẩy.")

# ==========================================
# 4. Đẩy lên TiDB Cloud (Automation)
# ==========================================
print("\n--- KẾT NỐI VÀ ĐẨY LÊN TiDB CLOUD ---")
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    print(" LỖI: Không tìm thấy biến môi trường DATABASE_URL! Nếu chạy local, hãy set biến này.")
    exit(1)

engine = create_engine(db_url)

try:
    # if_exists='append' thêm dòng mới vào db có sẵn
    df.to_sql('bank_reviews', con=engine, if_exists='append', index=False)
    print(" Thành công: Đã chèn dữ liệu tuần mới lên TiDB Cloud!")
except Exception as e:
    print(f" Lỗi quá trình đẩy SQL: {e}")
