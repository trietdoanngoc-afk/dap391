📸 HƯỚNG DẪN LẤY SCREENSHOT CHO BÁOCAO IEEE
==========================================================

## 🎯 Mục tiêu
- Tự động lấy screenshot Dashboard từ các state khác nhau
- Giúp làm minh chứng cho IEEE Report "Experimental Results"
- Tiết kiệm thời gian so với tự bấm trực tiếp

---

## 📋 Các Screenshot Sẽ Được Tự Động Lấy

### 1️⃣ **Overview Dashboard**
   - Hiển thị tất cả 4 KPI chính (Total Customers, Churn Rate, Avg Rating, ...)
   - **Dùng cho:** Phần "System Performance Overview"

### 2️⃣ **Model Results (93.9% Accuracy)**
   - Tab kết quả mô hình chi tiết
   - Hiển thị: Accuracy, Precision, Recall, F1-Score
   - **Dùng cho:** Phần "Quantitative Results" — conf mạnh cho nhận định 93.9%

### 3️⃣ **High Risk Customer (Rating 1-2⭐)**
   - Dự báo khách hàng CÓ THỂ CHURN
   - Input: Rating sao 2, Balance thấp, Tenure ngắn, Non-active
   - **Dùng cho:** Chứng minh model phát hiện khách hàng rủi ro chính xác

### 4️⃣ **Safe Customer (Rating 4-5⭐)**
   - Dự báo khách hàng AN TOÀN (Sẽ STY)
   - Input: Rating sao 5, Balance cao, Tenure lâu, Active member
   - **Dùng cho:** Chứng minh model không tạo alarm giả

### 5️⃣ **Feature Importance Insights**
   - Độ quan trọng các attributes (Rating: 88%)
   - **Dùng cho:** Phần định tính "Why customers churn"

---

## 🚀 CÁCH SỬ DỤNG

### Bước 1️⃣: Cài đặt Dependencies

```bash
# Nếu dùng Playwright (KHUYẾN NGHỊ)
pip install playwright
playwright install chromium

# Hoặc nếu dùng Selenium
pip install selenium webdriver-manager
```

### Bước 2️⃣: Khởi động Dashboard (Nếu chưa chạy)

```bash
# Terminal 1: Khởi động Streamlit
streamlit run streamlit_app.py --server.port 8000

# Terminal 2: Hoặc chạy HTML Dashboard tĩnh
# python -m http.server 8000 --directory dashboard
```

### Bước 3️⃣: Chạy Script Screenshot

```bash
python capture_screenshots.py
```

✅ **Điều gì sẽ xảy ra:**

1. Trình duyệt Chrome sẽ mở tự động
2. Điều hướng đến Dashboard
3. Tự động bấm các tab, điền form, nhấn button
4. Lấy screenshot tại mỗi stage
5. Lưu vào thư mục: `screenshots_for_report/`

---

## 📁 Output Structure

```
screenshots_for_report/
├── 01_overview_dashboard_HHMMSS.png       ← Tổng quan
├── 02_model_results_HHMMSS.png            ← Kết quả 93.9%
├── 03_customer_churn_high_risk_HHMMSS.png ← Khách hàng rủi ro
├── 04_customer_stay_safe_HHMMSS.png       ← Khách hàng an toàn
└── 05_feature_importance_HHMMSS.png       ← Feature importance
```

---

## 🎨 LƯU Ý VỀ FONT/ICON

✅ **Dashboard đã được cập nhật:**
- KPI values: 32px → 44px
- Chart titles: 15px → 18px
- Header: 24px → 32px
- Icons: 42px → 50px

→ Các con số sẽ **RỰC RỠ và DỄ ĐỌC** trên máy chiếu

---

## 🔧 CHỈNH SỬA SCENARIOS (Nếu cần)

File `capture_screenshots.py` có dict `SCENARIOS`:

```python
SCENARIOS = {
    "01_overview_dashboard": {
        "name": "📊 Analytics Dashboard Overview",
        "actions": [
            ("wait_for_load", 2),
        ]
    },
    # ... thêm hoặc sửa theo nhu cầu
}
```

**Action Types Có sẵn:**
- `("wait_for_load", seconds)` → Chờ N giây
- `("click_tab", "emoji")` → Bấm tab
- `("fill_form", {...})` → Điền form
- `("click_button", "text")` → Bấm button
- `("scroll_to", "text")` → Scroll đến section

---

## ⚠️ TROUBLESHOOTING

### ❌ "Dashboard not found" (localhost:8000)
→ Kiểm tra Streamlit đang chạy: `streamlit run streamlit_app.py --server.port 8000`

### ❌ "Playwright not installed"
→ Chạy: `pip install playwright && playwright install chromium`

### ❌ Screenshot ra toàn trắng/đen
→ Tăng `wait_for_load` time trong SCENARIOS:
```python
("wait_for_load", 4),  # Tăng từ 2 lên 4
```

### ❌ Form input không được điền
→ Kiểm tra selectors trong `selectors = {...}` — có thể cần update

---

## 💡 TIPS CHO BÀO CÁO IEEE

### 👉 Những gì nên hiển thị:

**Screenshot 1: Overview**
- "Toàn bộ hệ thống xử lý X,XXX khách hàng"

**Screenshot 2: Results**
- "Accuracy đạt 93.9% — tuy thấp hơn baseline 99%+ nhưng THỰC TẾ hơn vì chúng tôi CHUẨN BỊ noise 5-7% (xem train_model.py dòng 99-116)"

**Screenshot 3 & 4: Predictions**
- "Ví dụ minh họa — Model phân loại chính xác khách hàng rủi cao vs an toàn"

**Screenshot 5: Feature Importance**
- "Rating là yếu tố #1 (88%) nhưng không phải duy nhất — 16 features tổng hợp"

---

## 📝 SCRIPT FILES LIÊN QUAN

| File | Mục đích |
|------|---------|
| `capture_screenshots.py` | Script tự động lấy screenshot |
| `train_model.py` (dòng ~99-116) | Phần "Realistic Noise Injection" — GIẢI THÍCH |
| `dashboard/index.html` | Giao diện Dashboard (Font size + icons đã tăng) |
| `streamlit_app.py` | Backend Streamlit (nếu dùng Streamlit) |

---

## 🎬 DEMO FLOW

```
1. Chạy capture_screenshots.py
   ↓
2. Chrome mở → Dashboard load
   ↓
3. Tab 1: Overview → Screenshot
   ↓
4. Tab 2: Results → Screenshot (Thấy 93.9%)
   ↓
5. Tab 3: Prediction
   ├─ Điền: Rating 2⭐ → Dự báo CHURN → Screenshot
   ├─ Điền: Rating 5⭐ → Dự báo STY → Screenshot
   ↓
6. Scroll & Capture: Feature Importance
   ↓
7. ✅ Xong! Mở folder screenshots/ → Copy vào Report
```

---

## ❓ CẦN GIÚP?

Nếu gặp lỗi, kiểm tra:
1. Dashboard đang chạy (`localhost:8000`)?
2. Playwright/Selenium cài đúng?
3. Có lỗi gì trong browser console?

Chạy lại với verbose output:
```bash
python capture_screenshots.py 2>&1 | tee screenshot_log.txt
```

---

✅ **CHỦ YẾU**: Sau khi lấy screenshot, hãy **CHỊU KHẢO** chúng trong Report
   - Captions rõ ràng
   - Nhấn mạnh accuracy 93.9% + "noise injection for realism"
   - Explain Feature Importance: Rating 88% + 15 factors còn lại

**Good luck với IEEE submission! 🚀**
