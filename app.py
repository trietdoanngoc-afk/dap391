import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from sqlalchemy import create_engine
from config import TIDB_CONFIG

st.set_page_config(page_title="Interactive Bank Churn Dashboard", layout="wide")

# =====================================================================
# BƯỚC 1: SETUP & DATA LOADING
# =====================================================================
@st.cache_data(ttl=3600, show_spinner="Đang kéo dữ liệu từ TiDB Cloud...")
def load_data():
    """Load data directly from TiDB Cloud."""
    cfg = TIDB_CONFIG
    
    connection_string = (
        f"mysql+mysqlconnector://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    
    ssl_args = {
        "ssl_ca": cfg["ca_path"],
        "ssl_verify_cert": True,
    }
    
    engine = create_engine(connection_string, connect_args=ssl_args)
    
    try:
        query = f"SELECT * FROM {cfg['table']}"
        df = pd.read_sql(query, con=engine)
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối CSDL TiDB: {e}")
        return pd.DataFrame()
    finally:
        engine.dispose()

# Binning logic
def preprocess_for_dashboard(df):
    if df.empty:
        return df
        
    df_plot = df.copy()
    
    # Phân nhóm Tuổi
    age_bins = [18, 25, 35, 45, 100]
    age_labels = ['18-25', '25-35', '35-45', '45+']
    df_plot['age_group'] = pd.cut(df_plot['age'], bins=age_bins, labels=age_labels, right=False)
    
    # Phân nhóm Số dư (như yêu cầu mới)
    bal_bins = [-1, 1_000_000_000, 5_000_000_000, 10_000_000_000, float('inf')]
    bal_labels = ['< 1 tỷ', '1-5 tỷ', '5-10 tỷ', '> 10 tỷ']
    df_plot['balance_tier'] = pd.cut(df_plot['balance'], bins=bal_bins, labels=bal_labels)
    
    # VIP / High Value
    df_plot['is_vip'] = (df_plot['balance'] > 1_000_000_000).map({True: 'High Value (VIP)', False: 'Regular'})
    
    # Churn Label
    df_plot['churn_str'] = df_plot['churn'].map({0: 'Stayed', 1: 'Churned'})
    
    # Xử lý Thời gian (Giống 7_month_trend)
    time_col = None
    if 'date' in df_plot.columns:
        time_col = 'date'
    elif 'review_date' in df_plot.columns:
        time_col = 'review_date'
        
    if time_col:
        df_plot[time_col] = pd.to_datetime(df_plot[time_col])
        df_plot['month'] = df_plot[time_col].dt.month
        df_plot['month_yr'] = df_plot[time_col].dt.strftime('%m/%Y')
    elif 'review_month' in df_plot.columns:
        df_plot['month'] = df_plot['review_month']
        df_plot['month_yr'] = df_plot['review_month'].apply(lambda m: f"Tháng {int(m)}")
    else:
        df_plot['month_yr'] = "N/A"
        
    return df_plot

df_raw = load_data()
df_main = preprocess_for_dashboard(df_raw)

if df_main.empty:
    st.stop()

# =====================================================================
# BƯỚC 2: TẠO BỘ ĐIỀU KHIỂN (Sidebar Controller)
# =====================================================================
st.sidebar.title("Tùy chỉnh Hiển thị")

# Danh sách 6 biểu đồ yêu cầu
AVAILABLE_CHARTS = {
    "Tỷ lệ Churn giữa các Ngân hàng": "bank",
    "Xu hướng Rời bỏ theo 12 Tháng": "trend",
    "Tỷ lệ Rời bỏ theo Số dư": "balance",
    "Phân tích Nhóm VIP (> 1 Tỷ)": "vip",
    "Mật độ Rời bỏ theo Độ tuổi": "age",
    "Tỉ lệ Rời Bỏ Dựa Trên Số Năm Gắn Bó (Tenure)": "tenure"
}

st.sidebar.markdown("**Chọn biểu đồ bạn muốn hiển thị:**")
selected_chart_names = st.sidebar.multiselect(
    "Danh sách biểu đồ:",
    options=list(AVAILABLE_CHARTS.keys()),
    default=list(AVAILABLE_CHARTS.keys())
)
selected_chart_keys = [AVAILABLE_CHARTS[name] for name in selected_chart_names]

# =====================================================================
# BƯỚC 3 & 4: DASHBOARD LAYOUT VÀ LỌC
# =====================================================================
st.title("Phân Tích Khách Hàng Rời Bỏ")

# Global Filter (Chọn Ngân hàng) ở trên cùng
all_banks = sorted(df_main["bank_name"].dropna().unique().tolist())
selected_banks = st.multiselect(
    "Lọc thông tin theo Ngân hàng:",
    options=all_banks,
    default=all_banks
)

if not selected_banks:
    st.warning("Vui lòng chọn ít nhất một ngân hàng.")
    st.stop()

df_filtered = df_main[df_main["bank_name"].isin(selected_banks)]

# Metrics Tổng quan thiết kế đẹp hơn
st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    padding: 5% 5% 5% 10%;
    border-radius: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Tổng Số Khách Hàng", f"{len(df_filtered):,}")
col_m2.metric("Tỷ Lệ Rời Bỏ Trung Bình", f"{df_filtered['churn'].mean() * 100:.1f}%")
col_m3.metric("Số Ngân Hàng Được Chọn", len(selected_banks))

st.markdown("---")

COLOR_STAYED = "#3498db"
COLOR_CHURNED = "#e74c3c"
COLOR_MAP = {"Stayed": COLOR_STAYED, "Churned": COLOR_CHURNED}
CHART_TEMPLATE = "plotly_white"

# =====================================================================
# RENDER LOGIC CHO 6 CHART (Plotly)
# =====================================================================

def render_bank():
    st.subheader("Tỷ lệ Churn giữa các Ngân hàng")
    bank_churn = df_filtered.groupby("bank_name")["churn"].mean().reset_index()
    bank_churn["churn"] *= 100
    bank_churn = bank_churn.sort_values(by="churn", ascending=True)
    fig = px.bar(bank_churn, x="churn", y="bank_name", orientation='h',
                 color_discrete_sequence=["#e74c3c"],
                 labels={"churn": "Tỷ lệ Rời bỏ (%)", "bank_name": "Ngân hàng"},
                 text_auto=".1f", template=CHART_TEMPLATE)
    fig.update_layout(xaxis=dict(range=[0, max(bank_churn["churn"])*1.2 if max(bank_churn["churn"]) > 0 else 100]))
    fig.update_traces(marker_line_width=1, marker_line_color="darkred", opacity=0.85)
    st.plotly_chart(fig, use_container_width=True)

def render_trend():
    st.subheader("Xu hướng Rời bỏ theo 12 Tháng")
    
    # Init 12 months
    trend = pd.DataFrame({"month": range(1, 13)})
    
    if "month" in df_filtered.columns:
        monthly = df_filtered.groupby("month")["churn"].mean().reset_index()
        monthly["churn"] *= 100
        # Merge to ensure all 12 months exist
        trend = trend.merge(monthly, on="month", how="left").fillna(0)
        
    else:
        trend["churn"] = 0.0
        
    fig = px.line(trend, x="month", y="churn", markers=True,
                  labels={"month": "Tháng", "churn": "Tỷ lệ Rời bỏ (%)"}, template=CHART_TEMPLATE)
    fig.update_traces(line_color="#e74c3c", line_width=4, marker={"size": 10, "color": "darkred", "line": {"width": 2, "color": "white"}})
    fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
    st.plotly_chart(fig, use_container_width=True)

def render_balance():
    st.subheader("Tỷ lệ Rời bỏ theo Mức Số dư")
    bal_churn = df_filtered.groupby("balance_tier", observed=False)["churn"].mean().reset_index()
    bal_churn["churn"] *= 100
    fig = px.bar(bal_churn, x="balance_tier", y="churn", color="balance_tier",
                 color_discrete_sequence=["#bdc3c7", "#3498db", "#e67e22", "#c0392b"],
                 labels={"balance_tier": "Mức Số dư (VND)", "churn": "Tỷ lệ Rời bỏ (%)"},
                 text_auto=".1f", template=CHART_TEMPLATE)
    fig.update_traces(marker_line_width=1, marker_line_color="black", opacity=0.9)
    st.plotly_chart(fig, use_container_width=True)

def render_vip():
    st.subheader("Phân nhóm Khách hàng VIP (> 1 Tỷ)")
    vip_churn = df_filtered.groupby("is_vip")["churn"].mean().reset_index()
    vip_churn["churn"] *= 100
    fig = px.bar(vip_churn, x="is_vip", y="churn", color="is_vip",
                 color_discrete_map={'High Value (VIP)': '#f1c40f', 'Regular': '#7f8c8d'},
                 labels={"is_vip": "Phân khúc", "churn": "Tỷ lệ Rời bỏ (%)"},
                 text_auto=".1f", template=CHART_TEMPLATE)
    fig.update_traces(marker_line_width=1, marker_line_color="black", opacity=0.9)
    st.plotly_chart(fig, use_container_width=True)

def render_age():
    st.subheader("Mật độ Độ tuổi Khách hàng Rời bỏ")
    fig = px.histogram(df_filtered, x="age_group", color="churn_str",
                       color_discrete_map=COLOR_MAP, barmode="group",
                       category_orders={"age_group": ['18-25', '25-35', '35-45', '45+']},
                       labels={"age_group": "Nhóm Tuổi", "count": "Số lượng", "churn_str": "Trạng thái"},
                       text_auto=True, template=CHART_TEMPLATE)
    fig.update_traces(marker_line_width=1, marker_line_color="black", opacity=0.85)
    st.plotly_chart(fig, use_container_width=True)

def render_tenure():
    st.subheader("Tỉ lệ Rời Bỏ Dựa Trên Số Năm Gắn Bó (Tenure)")
    if "tenure" in df_filtered.columns:
        tenure_churn = df_filtered.groupby("tenure")["churn"].mean().reset_index()
        tenure_churn["churn"] *= 100
        fig = px.line(tenure_churn, x="tenure", y="churn", markers=True,
                      labels={"tenure": "Số năm gắn bó (Tenure)", "churn": "Tỷ lệ Rời bỏ (%)"}, template=CHART_TEMPLATE)
        fig.update_traces(line_color="#9b59b6", line_width=4, marker={"size": 8, "color": "purple", "line": {"width": 2, "color": "white"}})
        fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Không có dữ liệu Tenure.")

# Ánh xạ key chức năng
RENDER_FUNCS = {
    "bank": render_bank,
    "age": render_age,
    "balance": render_balance,
    "vip": render_vip,
    "trend": render_trend,
    "tenure": render_tenure
}

# Lưới 2 Cột
cols = st.columns(2)

valid_keys = [k for k in selected_chart_keys if k in RENDER_FUNCS]
for idx, key in enumerate(valid_keys):
    with cols[idx % 2]:
        RENDER_FUNCS[key]()

if not selected_chart_keys:
    st.info("Hãy chọn biểu đồ ở Menu bên trái.")
