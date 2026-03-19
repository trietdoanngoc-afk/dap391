import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent / "eda_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLOR_STAYED = "#3498db"
COLOR_CHURNED = "#e74c3c"
COLOR_MAP = {"Stayed": COLOR_STAYED, "Churned": COLOR_CHURNED}

def load_data():
    data_dir = Path(__file__).parent / "data" / "processed"
    xlsx_files = sorted(data_dir.glob("merged_all_reviews*.xlsx"))
    # Skip frozen files (they are reserved for run_eda.py only)
    xlsx_files = [f for f in xlsx_files if "FROZEN" not in f.name]
    if not xlsx_files:
        print("No processed data found!")
        return pd.DataFrame()
    return pd.read_excel(xlsx_files[-1], engine="openpyxl")

def preprocess(df):
    if df.empty: return df
    df_plot = df.copy()
    
    # Bins
    df_plot['age_group'] = pd.cut(df_plot['age'], bins=[18, 25, 35, 45, 100], labels=['18-25', '25-35', '35-45', '45+'], right=False)
    df_plot['balance_tier'] = pd.cut(df_plot['balance'], bins=[-1, 1_000_000_000, 5_000_000_000, 10_000_000_000, float('inf')], 
                                     labels=['< 1 tỷ', '1-5 tỷ', '5-10 tỷ', '> 10 tỷ'])
    df_plot['is_vip'] = (df_plot['balance'] > 1_000_000_000).map({True: 'High Value (VIP)', False: 'Regular'})
    df_plot['churn_str'] = df_plot['churn'].map({0: 'Stayed', 1: 'Churned'})
    
    if 'review_date' in df_plot.columns:
        df_plot['review_date'] = pd.to_datetime(df_plot['review_date'])
        df_plot['month'] = df_plot['review_date'].dt.month
        df_plot['month_yr'] = df_plot['review_date'].dt.strftime('%m/%Y')
    elif 'review_month' in df_plot.columns:
        df_plot['month'] = df_plot['review_month']
        df_plot['month_yr'] = df_plot['review_month'].apply(lambda m: f"Tháng {int(m)}")
    else:
        df_plot['month_yr'] = "N/A"
    return df_plot

def main():
    print("Loading data...")
    df_raw = load_data()
    df = preprocess(df_raw)
    if df.empty: return

    print("Generating 9 charts...")
    
    # 1. Churn Pie
    fig1 = px.pie(df, names='churn_str', color='churn_str', color_discrete_map=COLOR_MAP, hole=0.4, title="1. Churn Pie Chart")
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.write_image(str(OUTPUT_DIR / "1_Churn_Pie.png"), width=800, height=600)
    print(" Saved 1_Churn_Pie.png")

    # 2. Churn by Bank (Bar)
    bank_churn = df.groupby("bank_name")["churn"].mean().reset_index()
    bank_churn["churn"] *= 100
    bank_churn = bank_churn.sort_values(by="churn", ascending=True)
    fig2 = px.bar(bank_churn, x="churn", y="bank_name", orientation='h', color_discrete_sequence=["#e74c3c"],
                  labels={"churn": "Tỷ lệ Rời bỏ (%)", "bank_name": "Ngân hàng"}, title="2. Churn by Bank")
    fig2.update_layout(xaxis=dict(range=[0, max(bank_churn["churn"])*1.2 if max(bank_churn["churn"]) > 0 else 100]))
    fig2.write_image(str(OUTPUT_DIR / "2_Churn_by_Bank.png"), width=1000, height=600)
    print(" Saved 2_Churn_by_Bank.png")

    # 3. Age Analysis (Histogram + hue)
    fig3 = px.histogram(df, x="age_group", color="churn_str", color_discrete_map=COLOR_MAP, barmode="group",
                        category_orders={"age_group": ['18-25', '25-35', '35-45', '45+']},
                        labels={"age_group": "Nhóm Tuổi", "count": "Số lượng", "churn_str": "Trạng thái"},
                        title="3. Age Analysis (Histogram)")
    fig3.write_image(str(OUTPUT_DIR / "3_Age_Analysis.png"), width=900, height=600)
    print(" Saved 3_Age_Analysis.png")

    # 4. Gender Analysis (Bar)
    if "gender" in df.columns:
        gender_churn = df.groupby("gender")["churn"].mean().reset_index()
        gender_churn["churn"] *= 100
        fig4 = px.bar(gender_churn, x="gender", y="churn", color="gender", color_discrete_sequence=["#9b59b6", "#34495e"],
                      labels={"gender": "Giới tính", "churn": "Tỷ lệ Rời bỏ (%)"}, title="4. Gender Analysis")
        fig4.write_image(str(OUTPUT_DIR / "4_Gender_Analysis.png"), width=800, height=600)
        print(" Saved 4_Gender_Analysis.png")

    # 5. Balance Tiers (Bar)
    bal_churn = df.groupby("balance_tier", observed=False)["churn"].mean().reset_index()
    bal_churn["churn"] *= 100
    fig5 = px.bar(bal_churn, x="balance_tier", y="churn", color="balance_tier",
                  color_discrete_sequence=["#bdc3c7", "#3498db", "#e67e22", "#c0392b"],
                  labels={"balance_tier": "Mức Số dư", "churn": "Tỷ lệ Rời bỏ (%)"}, title="5. Balance Tiers")
    fig5.write_image(str(OUTPUT_DIR / "5_Balance_Tiers.png"), width=900, height=600)
    print(" Saved 5_Balance_Tiers.png")

    # 6. High Value VIP (Bar)
    vip_churn = df.groupby("is_vip")["churn"].mean().reset_index()
    vip_churn["churn"] *= 100
    fig6 = px.bar(vip_churn, x="is_vip", y="churn", color="is_vip",
                  color_discrete_map={'High Value (VIP)': '#f1c40f', 'Regular': '#7f8c8d'},
                  labels={"is_vip": "Phân khúc", "churn": "Tỷ lệ Rời bỏ (%)"}, title="6. High Value VIP Analysis")
    fig6.write_image(str(OUTPUT_DIR / "6_High_Value_VIP.png"), width=800, height=600)
    print(" Saved 6_High_Value_VIP.png")

    # 7. Trend (Line chart 12 tháng)
    if "month_yr" in df.columns:
        trend = df.groupby("month_yr")["churn"].mean().reset_index()
        trend["churn"] *= 100
        if 'month' in df.columns:
            trend_orig = df.groupby(["month", "month_yr"])["churn"].mean().reset_index()
            trend_orig = trend_orig.sort_values("month")
            trend["month_yr"] = trend_orig["month_yr"]
            trend["churn"] = trend_orig["churn"] * 100
            
        fig7 = px.line(trend, x="month_yr", y="churn", markers=True,
                       labels={"month_yr": "Thời gian", "churn": "Tỷ lệ Rời bỏ (%)"}, title="7. 12-Month Trend")
        fig7.update_traces(line_color="#e74c3c", line_width=4, marker=dict(size=10))
        fig7.write_image(str(OUTPUT_DIR / "7_Trend.png"), width=1000, height=600)
        print(" Saved 7_Trend.png")

    # 8. Products Usage (Bar) — thêm cột No Use (0)
    if "products_number" in df.columns:
        prod_churn = df.groupby("products_number")["churn"].mean().reset_index()
        prod_churn["churn"] *= 100
        # Thêm hàng No Use (0 sản phẩm) nếu chưa có
        if 0 not in prod_churn["products_number"].values:
            no_use = pd.DataFrame({"products_number": [0], "churn": [0.0]})
            prod_churn = pd.concat([no_use, prod_churn], ignore_index=True)
        prod_churn = prod_churn.sort_values("products_number")
        # Label rõ ràng
        label_map = {0: "No Use", 1: "1 SP", 2: "2 SP", 3: "3 SP", 4: "4 SP", 5: "5 SP"}
        prod_churn["label"] = prod_churn["products_number"].map(label_map).fillna(prod_churn["products_number"].astype(str))
        fig8 = px.bar(prod_churn, x="label", y="churn", color="products_number",
                      color_continuous_scale="Viridis",
                      labels={"label": "Số Sản Phẩm (Products)", "churn": "Tỷ lệ Rời bỏ (%)", "products_number": "Số SP"},
                      title="8. Products Usage")
        fig8.update_layout(xaxis_type="category")
        fig8.write_image(str(OUTPUT_DIR / "8_Products_Usage.png"), width=800, height=600)
        print(" Saved 8_Products_Usage.png")

    # 9. Correlation Heatmap
    numeric_cols = ["age", "balance", "credit_score", "tenure", "products_number", "rating", "churn"]
    cols_exist = [c for c in df.columns if c in numeric_cols and pd.api.types.is_numeric_dtype(df[c])]
    if len(cols_exist) > 1:
        corr = df[cols_exist].corr()
        fig9 = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", origin="lower", title="9. Correlation Heatmap")
        fig9.write_image(str(OUTPUT_DIR / "9_Correlation_Heatmap.png"), width=1000, height=800)
        print(" Saved 9_Correlation_Heatmap.png")

    print(f"\n✅ All 9 charts successfully exported to {OUTPUT_DIR}\\")

if __name__ == "__main__":
    main()
