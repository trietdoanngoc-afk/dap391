# 🏦 Hệ Thống Dự Báo Rời Bỏ Khách Hàng Ngân Hàng (Bank Churn)

Dự án cuối kỳ môn **DAP391** - Phân tích dữ liệu & Học máy (FPTU Da Nang).

## 🌟 Tính năng nổi bật
* **Dự báo Real-time:** Sử dụng mô hình **Random Forest (300 Trees)** để dự đoán xác suất rời bỏ.
* **Dashboard trực quan:** Hiển thị ma trận rủi ro, biểu đồ quan trọng (Feature Importance) bằng **Chart.js**.
* **Xử lý dữ liệu:** Áp dụng kỹ thuật **SMOTE** để cân bằng dữ liệu cực kỳ hiệu quả.

## 🛠️ Stack công nghệ
* **Backend:** FastAPI (Python) chạy tại `localhost:8000`.
* **Frontend:** HTML/CSS/JS thuần (Vanilla) - gọn nhẹ, tốc độ cao.
* **Database:** TiDB Cloud (MySQL compatible).

## 🚀 Hướng dẫn chạy nhanh
1. Cài đặt môi trường: `pip install -r requirements.txt`
2. Chạy Server: `uvicorn main:app --reload`
3. Mở file `dashboard/index.html` bằng trình duyệt để bắt đầu trải nghiệm.

---
**Sinh viên thực hiện:** Đoàn Ngọc Triết (trietdoanngoc-afk)
