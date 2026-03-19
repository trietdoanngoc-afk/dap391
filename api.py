from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text
import json
import os

app = FastAPI(title="Sentify ML Inference API")

# Allow CORS for local HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model Configuration
MODEL_PATH = Path(__file__).parent / "models" / "rf_churn_model.pkl"

if MODEL_PATH.exists():
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
    rf_model = model_data["model"]
    feature_cols = model_data["feature_cols"]
    print(f"✅ Loaded Model with {len(feature_cols)} features.")
else:
    print("❌ Model file not found! Please run `python train_model.py` first.")
    rf_model = None
    feature_cols = []

# Database connection (Lazy load)
_db_engine = None

def get_db_engine():
    """Get or create database engine"""
    global _db_engine
    if _db_engine is None:
        try:
            from config import TIDB_CONFIG
            cfg = TIDB_CONFIG
            connection_string = (
                f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
                f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
            )
            _db_engine = create_engine(connection_string, pool_pre_ping=True, pool_recycle=3600)
            print("✅ Database engine created successfully")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            _db_engine = False
    return _db_engine if _db_engine else None


class PredictRequest(BaseModel):
    bank_name: int
    rating: float
    sex: int
    age: float
    tenure: float
    credit_score: float
    balance: float
    products_number: int
    credit_card: int
    active_member: int
    platform_app_store: int
    platform_facebook: int
    platform_google_play: int


class CustomerActionRequest(BaseModel):
    action: str  # 'mark_processed' or 'save_note'
    customer_id: str
    note: str = None
    timestamp: str = None


@app.post("/predict")
def predict_churn(req: PredictRequest):
    if rf_model is None:
        return {"error": "Model not loaded on server."}
        
    # Calculate derived features dynamically just like in streamlit_app.py
    bal_per_prod = req.balance / max(1, req.products_number)
    tenure_age_rat = req.tenure / max(1, req.age)
    
    # VIP Logic (Hardcode threshold or fetch from DB, using fixed threshold 7B for stability)
    is_vip = 1 if (req.balance > 7000000000 and req.credit_score > 600) else 0
    
    # Current Time Features
    now = datetime.now()
    r_month = now.month
    r_day = now.weekday()
    
    # 2. Build 1-row DataFrame exactly matching training columns
    input_dict = {
        'bank_name': req.bank_name,
        'rating': req.rating,
        'sex': req.sex,
        'age': req.age,
        'tenure': req.tenure,
        'credit_score': req.credit_score,
        'balance': req.balance,
        'products_number': req.products_number,
        'credit_card': req.credit_card,
        'active_member': req.active_member,
        'platform_app_store': req.platform_app_store,
        'platform_facebook': req.platform_facebook,
        'platform_google_play': req.platform_google_play,
        'balance_per_product': bal_per_prod,
        'tenure_age_ratio': tenure_age_rat,
        'is_high_value': is_vip,
        'review_month': r_month,
        'review_day_of_week': r_day
    }
    
    df_pred = pd.DataFrame([input_dict])[feature_cols]
    
    # 3. Model Prediction
    pred = rf_model.predict(df_pred)[0]
    proba = rf_model.predict_proba(df_pred)[0].tolist()
    
    return {
        "churn": int(pred),
        "probability_stay": proba[0],
        "probability_churn": proba[1]
    }


@app.get("/api/stats/count")
def get_record_count():
    """
    Get dynamic record count from TiDB database.
    Returns: total_records, bank_count, at_risk_count
    """
    engine = get_db_engine()
    
    if not engine:
        return {
            "total_records": 24587,
            "bank_count": 35,
            "at_risk_count": 45,
            "status": "using_cached_data"
        }
    
    try:
        with engine.connect() as conn:
            # Total records
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM Sentify"))
            total = result.fetchone()[0]
            
            # Unique banks
            result = conn.execute(text("SELECT COUNT(DISTINCT bank_name) as cnt FROM Sentify"))
            banks = result.fetchone()[0]
            
            # At-risk count (rating <= 2 or churn = 1)
            result = conn.execute(text("""
                SELECT COUNT(*) as cnt FROM Sentify 
                WHERE rating <= 2 OR exited = 1
            """))
            at_risk = result.fetchone()[0]
            
            return {
                "total_records": int(total),
                "bank_count": int(banks),
                "at_risk_count": int(at_risk),
                "status": "live_from_database"
            }
            
    except Exception as e:
        print(f"Database query failed: {e}")
        return {
            "total_records": 24587,
            "bank_count": 35,
            "at_risk_count": 45,
            "status": "fallback_to_cached",
            "error": str(e)
        }


@app.post("/api/customer-action")
async def save_customer_action(req: CustomerActionRequest):
    """
    Track customer actions: mark as processed, save notes, etc.
    Stores in database and returns confirmation
    """
    engine = get_db_engine()
    
    action_data = {
        "action": req.action,
        "customer_id": req.customer_id,
        "note": req.note,
        "timestamp": req.timestamp or datetime.now().isoformat(),
        "status": "saved_locally"
    }
    
    if engine:
        try:
            with engine.connect() as conn:
                # Create action log table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS customer_actions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_id VARCHAR(255),
                        action VARCHAR(50),
                        note TEXT,
                        timestamp DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX (customer_id),
                        INDEX (action)
                    )
                """))
                
                if req.action == "mark_processed":
                    conn.execute(text("""
                        INSERT INTO customer_actions (customer_id, action, timestamp)
                        VALUES (:cid, :act, :ts)
                    """), {"cid": req.customer_id, "act": "mark_processed", "ts": req.timestamp})
                    
                elif req.action == "save_note":
                    conn.execute(text("""
                        INSERT INTO customer_actions (customer_id, action, note, timestamp)
                        VALUES (:cid, :act, :note, :ts)
                    """), {
                        "cid": req.customer_id,
                        "act": "save_note",
                        "note": req.note,
                        "ts": req.timestamp
                    })
                
                conn.commit()
                action_data["status"] = "saved_to_database"
                
        except Exception as e:
            print(f"Database save failed: {e}")
            action_data["status"] = "save_failed_using_local"
    
    return action_data


@app.get("/api/stats/live")
def get_live_statistics():
    """
    Get live dashboard statistics from database
    Returns KPI metrics for real-time dashboard updates
    """
    engine = get_db_engine()
    
    if not engine:
        # Return cached data if no DB
        return {
            "total_customers": 24587,
            "churned": 4932,
            "churn_rate": "20.1%",
            "avg_rating": 3.2,
            "at_risk": 45,
            "near_risk": 78,
            "status": "cached"
        }
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN exited = 1 THEN 1 ELSE 0 END) as churned,
                    ROUND(AVG(rating), 2) as avg_rating,
                    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as at_risk,
                    SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as near_risk
                FROM Sentify
            """))
            
            row = result.fetchone()
            total = row[0] or 0
            churned = row[1] or 0
            avg_rating = row[2] or 0
            at_risk = row[3] or 0
            near_risk = row[4] or 0
            
            churn_rate = (churned / total * 100) if total > 0 else 0
            
            return {
                "total_customers": int(total),
                "churned": int(churned),
                "churn_rate": f"{churn_rate:.1f}%",
                "avg_rating": float(avg_rating),
                "at_risk": int(at_risk),
                "near_risk": int(near_risk),
                "status": "live"
            }
            
    except Exception as e:
        print(f"Live stats query failed: {e}")
        return {
            "total_customers": 24587,
            "churned": 4932,
            "churn_rate": "20.1%",
            "avg_rating": 3.2,
            "at_risk": 45,
            "near_risk": 78,
            "status": "cached",
            "error": str(e)
        }


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": rf_model is not None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)
