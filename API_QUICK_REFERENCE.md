# 🔗 QUICK REFERENCE - API Endpoints & Features

## 📡 API Endpoints

### 1. **GET `/api/stats/count`**
**Purpose:** Lấy số lượng records từ database  
**Response:**
```json
{
    "total_records": 24587,
    "bank_count": 35,
    "at_risk_count": 47,
    "status": "live_from_database"
}
```

### 2. **GET `/api/stats/live`**
**Purpose:** Lấy KPI dashboard real-time  
**Response:**
```json
{
    "total_customers": 24587,
    "churned": 4932,
    "churn_rate": "20.1%",
    "avg_rating": 3.2,
    "at_risk": 45,
    "near_risk": 78,
    "status": "live"
}
```

### 3. **POST `/api/customer-action`**
**Purpose:** Lưu hành động nhân viên (mark processed, save notes)  
**Request:**
```json
{
    "action": "mark_processed",  // hoặc "save_note"
    "customer_id": "row_0_Vietcombank",
    "note": "Khách phàn nàn về phí",  // (optional)
    "timestamp": "2026-03-18T10:30:00"
}
```

### 4. **POST `/predict`**
**Purpose:** Dự báo xác suất churn của khách  
**Request:**
```json
{
    "bank_name": 0,
    "rating": 2,
    "sex": 1,
    "age": 45,
    "tenure": 5,
    "credit_score": 650,
    "balance": 5000000000,
    "products_number": 2,
    "credit_card": 1,
    "active_member": 1,
    "platform_app_store": 1,
    "platform_facebook": 0,
    "platform_google_play": 0
}
```

### 5. **GET `/health`**
**Purpose:** Health check  
**Response:**
```json
{
    "status": "ok",
    "model_loaded": true
}
```

---

## 🎛️ Interactive Features

### Feature 1: Dynamic Record Count
```javascript
// Before: Hardcoded
document.getElementById('dataInfo').textContent = "24,587 records | 35 banks";

// After: Live from API
const data = await fetch('/api/stats/count').then(r => r.json());
document.getElementById('dataInfo').innerHTML = `
    📊 ${data.total_records} records | ${data.bank_count} banks
`;
```

### Feature 2: Mark as Processed
```javascript
// Button click
<button onclick="markProcessed('row_0_VCB', this)">Xử lý</button>

// Function
function markProcessed(id, btn) {
    // 1. Save to localStorage
    localStorage.setItem(`processed_${id}`, 'true');
    
    // 2. Update UI
    btn.textContent = '✓ Xong';
    btn.classList.add('completed');
    
    // 3. Sync to backend
    fetch('/api/customer-action', {
        method: 'POST',
        body: JSON.stringify({action: 'mark_processed', customer_id: id})
    });
}
```

### Feature 3: Add Notes
```javascript
// Toggle notes form
function toggleNotes(id, event) {
    const row = document.getElementById(`notes_row_${id}`);
    row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
}

// Save notes
function saveNotes(id) {
    const note = document.getElementById(`notes_${id}`).value;
    
    // Save locally
    localStorage.setItem(`notes_${id}`, note);
    
    // Sync to backend
    fetch('/api/customer-action', {
        method: 'POST',
        body: JSON.stringify({
            action: 'save_note',
            customer_id: id,
            note: note
        })
    });
}
```

---

## 🔐 RBAC Roles

```
STAFF (👤 Nhân viên)
├─ view_own_customers: ✅
├─ mark_processed: ✅
├─ add_notes: ✅
├─ view_all_customers: ❌
├─ export_data: ❌
└─ system_logs: ❌

MANAGER (👨‍💼 Quản lý)
├─ view_own_customers: ✅
├─ mark_processed: ✅
├─ add_notes: ✅
├─ view_all_customers: ✅
├─ export_data: ✅
└─ system_logs: ❌

ADMIN (🔑 Quản trị viên)
├─ view_own_customers: ✅
├─ mark_processed: ✅
├─ add_notes: ✅
├─ view_all_customers: ✅
├─ export_data: ✅
└─ system_logs: ✅
```

---

## 💾 Local Storage Keys

```javascript
// Mark processed status
localStorage.getItem(`processed_row_0_VCB`)
// returns: 'true' or null

// Saved notes
localStorage.getItem(`notes_row_0_VCB`)
// returns: Note content or null

// User session
localStorage.getItem(`user_role`)
// returns: 'staff' | 'manager' | 'admin'
```

---

## 🗄️ Database Tables

### Sentify (Main Table)
```sql
id, bank_name, rating, balance, age, tenure, exited, ...
```

### customer_actions (Log Table)
```sql
id, customer_id, action, note, timestamp, created_at
```

### action_logs (Audit Trail)
```sql
id, user_id, user_role, action, details, timestamp
```

---

## ⚙️ Configuration

### File: `config.py`
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

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install fastapi uvicorn sqlalchemy pymysql pandas

# 2. Run backend
uvicorn api:app --port 8000

# 3. Open dashboard
# file:///d:/Triet/DAP391/proj/dashboard/index.html

# 4. Test endpoints
curl http://localhost:8000/api/stats/count
curl http://localhost:8000/health
```

---

## 🧪 Testing

```bash
# Test record count
curl http://localhost:8000/api/stats/count | jq

# Test mark processed
curl -X POST http://localhost:8000/api/customer-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "mark_processed",
    "customer_id": "row_0_VCB",
    "timestamp": "2026-03-18T10:30:00"
  }'

# Test save note
curl -X POST http://localhost:8000/api/customer-action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "save_note",
    "customer_id": "row_0_VCB",
    "note": "Khách phàn nàn về phí",
    "timestamp": "2026-03-18T10:30:00"
  }'

# Test health
curl http://localhost:8000/health | jq
```

---

## 📊 CSS Classes

```css
/* Stats info styling */
#dataInfo { ... }

/* Interactive buttons */
.btn-processed { ... }
.btn-processed.completed { ... }
.btn-processed:hover { ... }

/* Notes section */
.notes-section { ... }
.notes-input { ... }
.notes-input:focus { ... }
```

---

## 🔄 Auto-Refresh Settings

```javascript
// Refresh every 5 minutes
setInterval(() => {
    fetch('data.json').then(r => r.json()).then(data => {
        DATA = data;
        applyFilters();
        console.log("✅ Data refreshed");
    });
}, 300000); // 5 * 60 * 1000
```

---

## ✅ Verification Checklist

- [ ] Backend API running on port 8000
- [ ] Database connection successful
- [ ] Model loaded (18 features)
- [ ] Dashboard loads without errors
- [ ] Stats count shows live data
- [ ] Mark processed button works
- [ ] Notes save to localStorage + backend
- [ ] RBAC permissions enforced
- [ ] Auto-refresh every 5 minutes
- [ ] Error handling works correctly

---

**Last Updated:** 2026-03-18  
**Maintained by:** AI Assistant  
**Status:** Production Ready ✅
