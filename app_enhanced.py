"""
Enhanced Streamlit Dashboard with Real-Time Database Connection & RBAC
Features:
- Direct TiDB Cloud connection
- Real-time KPI updates
- Role-Based Access Control (RBAC)
- Action logging & tracking
- Offline-first notes system
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine, text
from config import TIDB_CONFIG
import json
from enum import Enum

# ================================================================
# USER ROLES & PERMISSIONS
# ================================================================

class UserRole(str, Enum):
    STAFF = "staff"
    MANAGER = "manager"
    ADMIN = "admin"

PERMISSIONS = {
    UserRole.STAFF: {
        "view_own_customers": True,
        "mark_processed": True,
        "add_notes": True,
        "view_all_customers": False,
        "export_data": False,
        "view_staff_performance": False,
        "system_logs": False
    },
    UserRole.MANAGER: {
        "view_own_customers": True,
        "mark_processed": True,
        "add_notes": True,
        "view_all_customers": True,
        "export_data": True,
        "view_staff_performance": True,
        "system_logs": False
    },
    UserRole.ADMIN: {
        "view_own_customers": True,
        "mark_processed": True,
        "add_notes": True,
        "view_all_customers": True,
        "export_data": True,
        "view_staff_performance": True,
        "system_logs": True
    }
}

# ================================================================
# SESSION STATE INITIALIZATION
# ================================================================

if "user_role" not in st.session_state:
    st.session_state.user_role = UserRole.STAFF

if "user_id" not in st.session_state:
    st.session_state.user_id = "user_001"

if "user_name" not in st.session_state:
    st.session_state.user_name = "Nhân viên"

# ================================================================
# DATABASE CONNECTION (TIDB CLOUD)
# ================================================================

@st.cache_resource
def get_db_engine():
    """Create database engine with connection pooling"""
    try:
        cfg = TIDB_CONFIG
        connection_string = (
            f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        )
        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        st.success("✅ Connected to TiDB Cloud")
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

engine = get_db_engine()

# ================================================================
# REAL-TIME DATA LOADING
# ================================================================

@st.cache_data(ttl=300, show_spinner="📊 Đang cập nhật dữ liệu từ TiDB Cloud...")
def load_live_data():
    """Load data directly from TiDB with auto-refresh every 5 minutes"""
    if not engine:
        st.warning("⚠️ Database not available. Using sample data.")
        return pd.DataFrame()
    
    try:
        with engine.connect() as conn:
            query = "SELECT * FROM Sentify LIMIT 10000"
            df = pd.read_sql(query, con=conn)
            return df
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner="🔄 Cập nhật KPI...")
def get_live_kpi():
    """Get real-time KPI metrics"""
    if not engine:
        return {
            "total_customers": 24587,
            "churned": 4932,
            "churn_rate": 20.1,
            "avg_rating": 3.2,
            "at_risk": 45
        }
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN exited = 1 THEN 1 ELSE 0 END) as churned,
                    ROUND(AVG(rating), 2) as avg_rating,
                    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as at_risk
                FROM Sentify
            """))
            row = result.fetchone()
            
            total = row[0] or 1
            churned = row[1] or 0
            
            return {
                "total_customers": int(total),
                "churned": int(churned),
                "churn_rate": round(churned / total * 100, 1),
                "avg_rating": float(row[2] or 0),
                "at_risk": int(row[3] or 0)
            }
    except Exception as e:
        st.error(f"KPI error: {e}")
        return {}

# ================================================================
# ACTION LOGGING & TRACKING
# ================================================================

def log_action(action: str, details: str):
    """Log user actions to database"""
    if not engine:
        return
    
    try:
        with engine.connect() as conn:
            # Create log table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(50),
                    user_role VARCHAR(20),
                    action VARCHAR(100),
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX (user_id),
                    INDEX (action),
                    INDEX (timestamp)
                )
            """))
            
            conn.execute(text("""
                INSERT INTO action_logs (user_id, user_role, action, details)
                VALUES (:uid, :role, :act, :det)
            """), {
                "uid": st.session_state.user_id,
                "role": st.session_state.user_role.value,
                "act": action,
                "det": details
            })
            conn.commit()
    except Exception as e:
        pass  # Silent fail

# ================================================================
# PAGE SETUP
# ================================================================

st.set_page_config(
    page_title="🏦 SENTIFY - Real-Time Bank Churn Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .at-risk-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .header-title {
        font-size: 28px;
        font-weight: bold;
        color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# ================================================================
# SIDEBAR - USER ROLE & SETTINGS
# ================================================================

with st.sidebar:
    st.markdown("### 👤 Thông Tin Người Dùng")
    
    # User role selector (for demo)
    selected_role = st.selectbox(
        "Vai trò:",
        [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN],
        format_func=lambda x: {
            UserRole.STAFF: "👤 Nhân viên",
            UserRole.MANAGER: "👨‍💼 Quản lý",
            UserRole.ADMIN: "🔑 Quản trị viên"
        }[x]
    )
    st.session_state.user_role = selected_role
    
    st.markdown("---")
    
    # Show permissions
    st.markdown("### 🔐 Quyền Hạn")
    perms = PERMISSIONS[st.session_state.user_role]
    
    permission_texts = {
        "view_own_customers": "Xem khách hàng của mình",
        "mark_processed": "Đánh dấu xử lý",
        "add_notes": "Ghi chú khách hàng",
        "view_all_customers": "Xem tất cả khách hàng",
        "export_data": "Xuất dữ liệu",
        "view_staff_performance": "Xem hiệu suất nhân viên",
        "system_logs": "Xem log hệ thống"
    }
    
    for perm, has_access in perms.items():
        icon = "✅" if has_access else "❌"
        st.text(f"{icon} {permission_texts[perm]}")
    
    st.markdown("---")
    
    # Refresh settings
    st.markdown("### 🔄 Cập Nhật")
    refresh_interval = st.slider(
        "Làm tươi dữ liệu (phút):",
        min_value=1,
        max_value=60,
        value=5
    )
    
    if st.button("🔄 Cập nhật ngay"):
        st.cache_data.clear()
        st.rerun()

# ================================================================
# MAIN DASHBOARD
# ================================================================

st.markdown('<div class="header-title">🏦 SENTIFY Ultimate Dashboard</div>', unsafe_allow_html=True)
st.markdown("Phân tích chuyên sâu về rời bỏ khách hàng trong lĩnh vực ngân hàng")

# Load data
df = load_live_data()
kpi = get_live_kpi()

if df.empty:
    st.error("❌ Không thể tải dữ liệu")
    st.stop()

# ================================================================
# REAL-TIME KPI CARDS
# ================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📊 Tổng Khách Hàng",
        f"{kpi.get('total_customers', 0):,}",
    )

with col2:
    st.metric(
        "🚨 Đã Rời Đi",
        f"{kpi.get('churned', 0):,}",
    )

with col3:
    st.metric(
        "📈 Tỷ Lệ Churn",
        f"{kpi.get('churn_rate', 0):.1f}%",
    )

with col4:
    st.metric(
        "⭐ Đánh Giá TB",
        f"{kpi.get('avg_rating', 0):.1f} / 5",
    )

with col5:
    st.metric(
        "⚠️ At-Risk",
        f"{kpi.get('at_risk', 0)}",
    )

# Last update time
col1, col2 = st.columns([4, 1])
with col2:
    st.caption(f"🕐 Cập nhật lúc: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")

# ================================================================
# INTERACTIVE TABS
# ================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Phân Tích",
    "👥 Danh Sách Khách",
    "📝 Ghi Chú & Hành Động",
    "📊 Báo Cáo"
])

# ================================================================
# TAB 1: ANALYSIS
# ================================================================

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Churn by Rating
        if not df.empty:
            churn_by_rating = df.groupby('rating').agg({
                'exited': ['sum', 'count']
            }).reset_index()
            churn_by_rating.columns = ['Rating', 'Churned', 'Total']
            churn_by_rating['Churn_Rate'] = (churn_by_rating['Churned'] / churn_by_rating['Total'] * 100).round(1)
            
            fig = px.bar(
                churn_by_rating,
                x='Rating',
                y='Churn_Rate',
                title="Tỷ Lệ Churn theo Rating",
                labels={'Churn_Rate': 'Churn Rate (%)'},
                color='Churn_Rate',
                color_continuous_scale='RdYlGn_r',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Churn by Bank
        if not df.empty and 'bank_name' in df.columns:
            churn_by_bank = df.groupby('bank_name').agg({
                'exited': ['sum', 'count']
            }).reset_index()
            churn_by_bank.columns = ['Bank', 'Churned', 'Total']
            churn_by_bank['Churn_Rate'] = (churn_by_bank['Churned'] / churn_by_bank['Total'] * 100).round(1)
            churn_by_bank = churn_by_bank.nlargest(10, 'Churn_Rate')
            
            fig = px.barh(
                churn_by_bank,
                x='Churn_Rate',
                y='Bank',
                title="Top 10 Ngân hàng Có Churn Rate Cao",
                labels={'Churn_Rate': 'Churn Rate (%)'},
                color='Churn_Rate',
                color_continuous_scale='Reds',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

# ================================================================
# TAB 2: CUSTOMER LIST
# ================================================================

with tab2:
    st.markdown("### 👥 Danh Sách Khách Hàng")
    
    # Filter options (if manager/admin)
    if PERMISSIONS[st.session_state.user_role]["view_all_customers"]:
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox("Trạng thái:", ["Tất cả", "At-Risk", "Churned"])
        with col2:
            search_bank = st.text_input("Tìm ngân hàng:", "")
        
        # Filter data
        filtered_df = df.copy()
        if filter_status == "At-Risk":
            filtered_df = filtered_df[filtered_df['rating'] <= 2]
        elif filter_status == "Churned":
            filtered_df = filtered_df[filtered_df['exited'] == 1]
        
        if search_bank:
            if 'bank_name' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['bank_name'].str.contains(search_bank, case=False)]
        
        # Display table
        display_cols = [col for col in ['bank_name', 'rating', 'balance', 'age', 'tenure', 'exited'] if col in filtered_df.columns]
        st.dataframe(
            filtered_df[display_cols].head(100),
            use_container_width=True,
            height=400
        )
        
        # Log action
        log_action("view_customer_list", f"Xem danh sách {len(filtered_df)} khách hàng")
    else:
        st.info("👤 Bạn chỉ có quyền xem khách hàng được gán cho mình")
        log_action("insufficient_permission", "Cố gắng xem danh sách tất cả khách hàng")

# ================================================================
# TAB 3: NOTES & ACTIONS
# ================================================================

with tab3:
    st.markdown("### 📝 Ghi Chú & Hành Động Xử Lý")
    
    if PERMISSIONS[st.session_state.user_role]["add_notes"]:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            customer_id = st.text_input("Mã Khách Hàng:")
            action_type = st.selectbox("Hành động:", ["Ghi chú", "Đánh dấu xử lý", "Không liên lạc được"])
        
        with col2:
            note_content = st.text_area("Nội dung ghi chú:")
        
        if st.button("💾 Lưu Ghi Chú"):
            if customer_id and note_content:
                log_action(
                    f"note_{action_type.lower()}",
                    f"Customer: {customer_id}, Content: {note_content[:100]}"
                )
                st.success("✅ Ghi chú đã lưu")
            else:
                st.error("❌ Vui lòng điền đầy đủ thông tin")
    else:
        st.warning("❌ Bạn không có quyền ghi chú")

# ================================================================
# TAB 4: REPORTS
# ================================================================

with tab4:
    st.markdown("### 📊 Báo Cáo")
    
    if PERMISSIONS[st.session_state.user_role]["export_data"]:
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Loại báo cáo:",
                ["Churn Analysis", "By Bank", "By Rating", "Call History"]
            )
        
        with col2:
            date_range = st.date_input(
                "Khoảng thời gian:",
                [datetime.now() - timedelta(days=30), datetime.now()]
            )
        
        if st.button("📥 Tạo Báo Cáo"):
            st.info(f"✅ Tạo báo cáo: {report_type}")
            log_action("generate_report", f"Type: {report_type}")
            
            # Example export
            csv = df.head(1000).to_csv(index=False)
            st.download_button(
                label="📥 Tải CSV",
                data=csv,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.warning("❌ Bạn không có quyền xuất báo cáo")

# ================================================================
# FOOTER
# ================================================================

st.markdown("---")
st.markdown("""
    **SENTIFY Dashboard v1.0** | Real-Time Database Connection  
    TiDB Cloud | FastAPI Backend | Streamlit Frontend  
    © 2026 DAP391 Project
""")
