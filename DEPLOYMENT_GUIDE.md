# 🚀 DEPLOYMENT & SETUP GUIDE

## Hướng Dẫn Triển Khai Hệ Thống Real-Time Dashboard

---

## 📋 Nội Dung

1. [Cài Đặt Dependencies](#1-cài-đặt-dependencies)
2. [Cấu Hình Database](#2-cấu-hình-tidb-cloud)
3. [Chạy Backend API](#3-chạy-backend-fastapi)
4. [Chạy Frontend Dashboard](#4-chạy-frontend-dashboard)
5. [Testing & Validation](#5-testing--validation)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Cài Đặt Dependencies

### Python Packages

```bash
# Tạo virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt
```

### File `requirements.txt`:

```
# Backend
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
pymysql==1.1.0
pandas==2.1.3

# Frontend (Optional)
streamlit==1.28.1
plotly==5.17.0

# Data Science
numpy==1.26.2
scikit-learn==1.3.2
pickle5==0.0.12
```

### Cài đặt:

```bash
pip install fastapi uvicorn sqlalchemy pymysql pandas streamlit plotly numpy scikit-learn
```

---

## 2. Cấu Hình TiDB Cloud

### Check File `config.py`:

```python
TIDB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "3x3Pw8kXsFE6rzh.root",
    "password": "i8iPou2WrM4FIGQn",
    "database": "Bank_Churn_Data",
    "table": "Sentify",
    "ca_path": str(Path(__file__).parent / "isrgrootx1.pem"),
}
```

### Test Database Connection:

```python
from sqlalchemy import create_engine, text
from config import TIDB_CONFIG

cfg = TIDB_CONFIG
connection_string = (
    f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
    f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
)
engine = create_engine(connection_string)

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM Sentify"))
    print(f"Total records: {result.fetchone()[0]}")
```

---

## 3. Chạy Backend FastAPI

### Start API Server:

```bash
cd /path/to/project
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

### Output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
✅ Loaded Model with 18 features.
✅ Database engine created successfully
```

### Test API Endpoints:

```bash
# Health check
curl http://localhost:8000/health
# Response: {"status":"ok","model_loaded":true}

# Get record count
curl http://localhost:8000/api/stats/count
# Response: {"total_records":24587,"bank_count":35,"at_risk_count":47,"status":"live_from_database"}

# Get live KPI
curl http://localhost:8000/api/stats/live
# Response: {"total_customers":24587,"churned":4932,"churn_rate":"20.1%",...}
```

---

## 4. Chạy Frontend Dashboard

### Option A: HTML Dashboard (Static)

```bash
# Đơn giản nhất - chỉ cần mở file HTML
# Mở browser tại: file:///d:/Triet/DAP391/proj/dashboard/index.html
```

**Lưu ý:** Để các API calls hoạt động, cần chạy backend API trước!

### Option B: Streamlit Dashboard (Interactive)

```bash
streamlit run app.py
```

Output:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Option C: Enhanced Streamlit with RBAC

```bash
streamlit run app_enhanced.py
```

---

## 5. Testing & Validation

### Test 5.1: Record Count (Dynamic)

```python
# Test dynamic counting
# Trước: "24,587 records" (hardcoded)
# Sau: Gọi API /api/stats/count → lấy từ database

import requests
response = requests.get('http://localhost:8000/api/stats/count')
data = response.json()
print(f"Total: {data['total_records']}")
print(f"At-Risk: {data['at_risk_count']}")
```

### Test 5.2: Customer Action Tracking

```python
# Test mark as processed
response = requests.post(
    'http://localhost:8000/api/customer-action',
    json={
        "action": "mark_processed",
        "customer_id": "row_0_Vietcombank",
        "timestamp": "2026-03-18T10:30:00"
    }
)
print(response.json())
# Response: {"action":"mark_processed","status":"saved_to_database"}
```

### Test 5.3: Notes Saving

```python
# Test save note
response = requests.post(
    'http://localhost:8000/api/customer-action',
    json={
        "action": "save_note",
        "customer_id": "row_0_Vietcombank",
        "note": "Khách phàn nàn về phí thẻ, cần giảm phí",
        "timestamp": "2026-03-18T10:30:00"
    }
)
print(response.json())
# Response: {"status":"saved_to_database"}
```

### Test 5.4: Interactive Buttons

1. **Mở HTML Dashboard:** `file:///d:/Triet/DAP391/proj/dashboard/index.html`
2. **Tìm hàng bất kỳ trong bảng**
3. **Nhấn nút "Xử lý"** → Nút chuyển thành "✓ Xong"
4. **Nhấn nút "📝 Note"** → Mở form ghi chú
5. **Nhập nội dung, nhấn "Lưu ghi chú"** → Dữ liệu lưu vào localStorage + database

---

## 6. Troubleshooting

### ❌ Lỗi: "Cannot connect to TiDB"

**Nguyên nhân:** Network issue hoặc credentials sai

**Giải pháp:**
```bash
# Test connection
ping gateway01.ap-southeast-1.prod.aws.tidbcloud.com

# Kiểm tra credentials trong config.py
python -c "from sqlalchemy import create_engine; engine = create_engine('mysql+pymysql://...'); print('OK')"
```

### ❌ Lỗi: "Model file not found"

**Giải pháp:**
```bash
# Đảm bảo model được train trước
python train_model.py

# Kiểm tra model path
ls models/rf_churn_model.pkl
```

### ❌ Lỗi: "API not responding"

**Giải pháp:**
```bash
# Kiểm tra port
netstat -an | grep 8000  # Windows: netstat -ano | findstr :8000

# Kill process nếu đang chạy
# Windows: taskkill /PID <PID> /F
# Linux: kill -9 <PID>

# Start API lại
uvicorn api:app --port 8000 --reload
```

### ❌ Lỗi: "CORS error"

**Giải pháp:** API đã setup CORS headers, nhưng kiểm tra lại nếu cần:

```python
# Trong api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 7. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE (Browser)                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  dashboard/index.html                                  │  │
│  │  - CSS: Stats info styling                             │  │
│  │  - JS: Dynamic record count, interactive buttons       │  │
│  │  - localStorage: Offline-first notes                   │  │
│  └────────┬─────────────────────────────────────┬─────────┘  │
└───────────┼─────────────────────────────────────┼────────────┘
            │                                     │
    ┌───────▼────────────┐         ┌─────────────▼──────────┐
    │ API Endpoint #1    │         │ API Endpoint #2        │
    │ /api/stats/count   │         │ /api/customer-action   │
    │ (GET)              │         │ (POST)                 │
    │ → Live record count│         │ → Save notes/actions   │
    └───────┬────────────┘         └──────────┬──────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           │
            ┌──────────────▼─────────────────┐
            │   Backend: FastAPI (api.py)    │
            │   - /predict                   │
            │   - /api/stats/*               │
            │   - /api/customer-action       │
            └──────────────┬─────────────────┘
                           │
            ┌──────────────▼─────────────────┐
            │  TiDB Cloud Database           │
            │  - Sentify (customer data)     │
            │  - customer_actions (logs)     │
            │  - action_logs (audit trail)   │
            └────────────────────────────────┘
```

---

## 8. Directory Structure

```
proj/
├── api.py                              # FastAPI backend
├── app.py                              # Streamlit app
├── app_enhanced.py                     # Streamlit with RBAC
├── config.py                           # Configuration
├── train_model.py                      # Model training
├── requirements.txt                    # Dependencies
├── dashboard/
│   ├── index.html                      # Main dashboard HTML
│   └── data.json                       # Sample data
├── models/
│   └── rf_churn_model.pkl              # Trained model
├── data/
│   └── processed/
│       └── merged_all_reviews.csv      # Training data
└── REAL_TIME_IMPLEMENTATION.md         # This guide
```

---

## 9. Khi Triển Khai Lên Production

### 9.1 Cấu Hình Gunicorn (instead of Uvicorn)

```bash
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

### 9.2 Cấu Hình Nginx Reverse Proxy

```nginx
upstream api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api;
    }
}
```

### 9.3 Enable SSL/TLS

```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d your_domain.com
```

### 9.4 Database Backup

```bash
# Regular backups
mysqldump -h gateway01.ap-southeast-1.prod.aws.tidbcloud.com \
  --user=3x3Pw8kXsFE6rzh.root \
  -p Bank_Churn_Data > backup_$(date +%Y%m%d).sql
```

---

## 10. Performance Tips

1. **Cache Strategies:**
   - @st.cache_data(ttl=300) → 5 min refresh
   - Database connection pooling
   - LocalStorage for client-side caching

2. **Database Optimization:**
   - Create indexes on `customer_id`, `action`, `timestamp`
   - Use LIMIT 10000 for initial queries
   - Archive old records regularly

3. **Frontend Optimization:**
   - Lazy load charts
   - Minimize API calls
   - Use pagination for large tables

---

## ✅ Checklist Trước Khi Triển Khai

- [ ] Database connection tested
- [ ] Model training completed
- [ ] API endpoints working
- [ ] Dashboard displaying correctly
- [ ] Interactive buttons functional
- [ ] Notes being saved
- [ ] RBAC permissions set
- [ ] Error handling implemented
- [ ] Security headers configured
- [ ] Backup strategy established

---

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Check logs: `tail -f api.log`
2. Test endpoints: `curl http://localhost:8000/health`
3. Verify database: Kết nối vào TiDB Console
4. Check browser console: F12 → Console tab

---

**Last Updated:** 2026-03-18  
**Version:** 1.0  
**Status:** Production Ready ✅
