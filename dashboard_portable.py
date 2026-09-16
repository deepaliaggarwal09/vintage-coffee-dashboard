"""
Vintage Coffee & Beverages Ltd - Business Analytics Dashboard (PORTABLE VERSION)
Academic Task 1 - MKT322 Advanced Business Analytics

This version reads from a bundled SQLite file (vintage_coffee.db) instead of a
live MySQL/XAMPP server, so it runs on ANY computer with just Python installed —
no XAMPP or MySQL setup required.

HOW TO RUN:
1. Put dashboard_portable.py AND vintage_coffee.db in the SAME folder.
2. Install packages (only needed once per computer):
       pip install streamlit plotly pandas
   (Note: no mysql-connector-python needed for this version!)
3. Run:
       python -m streamlit run dashboard_portable.py
4. It opens in your browser at http://localhost:8501
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Vintage Coffee & Beverages Ltd - Analytics Dashboard",
    page_icon="☕",
    layout="wide"
)

# -----------------------------------------------------------------------
# DATABASE CONNECTION (SQLite file bundled alongside this script)
# -----------------------------------------------------------------------
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vintage_coffee.db")

@st.cache_data(ttl=300)
def run_query(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# -----------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------
try:
    quarterly = run_query("SELECT * FROM quarterly_results ORDER BY quarter_end")
    annual = run_query("SELECT * FROM annual_pnl ORDER BY fiscal_year_end")
    balance = run_query("SELECT * FROM balance_sheet ORDER BY fiscal_year_end")
    cashflow = run_query("SELECT * FROM cash_flows ORDER BY fiscal_year_end")
    ratios = run_query("SELECT * FROM ratios ORDER BY fiscal_year_end")
    shareholding = run_query("SELECT * FROM shareholding_pattern ORDER BY quarter_end")
    peers = run_query("SELECT * FROM peer_comparison ORDER BY roce_pct DESC")
except Exception as e:
    st.error(f"Could not open vintage_coffee.db. Make sure it is in the SAME "
              f"folder as this script.\n\nError: {e}")
    st.stop()

# -----------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------
st.title("☕ Vintage Coffee & Beverages Ltd — Business Analytics Dashboard")
st.caption("Academic Task 1 | MKT322 Advanced Business Analytics")

# -----------------------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------------------
latest = quarterly.iloc[-1]
previous = quarterly.iloc[-2]

def pct_change(curr, prev):
    return round(((curr - prev) / prev) * 100, 1) if prev != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Quarter Sales (Cr)", f"₹{latest['sales_cr']:.0f}",
            f"{pct_change(latest['sales_cr'], previous['sales_cr'])}% QoQ")
col2.metric("Net Profit (Cr)", f"₹{latest['net_profit_cr']:.0f}",
            f"{pct_change(latest['net_profit_cr'], previous['net_profit_cr'])}% QoQ")
col3.metric("Operating Margin (OPM%)", f"{latest['opm_pct']:.1f}%",
            f"{round(latest['opm_pct'] - previous['opm_pct'], 1)} pts")
col4.metric("EPS (₹)", f"{latest['eps_rs']:.2f}",
            f"{pct_change(latest['eps_rs'], previous['eps_rs'])}% QoQ")

st.divider()

# -----------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Revenue & Profit", "🏦 Balance Sheet & Cash", "⚙️ Efficiency Ratios",
     "👥 Shareholding", "🏆 Peer Comparison"]
)

with tab1:
    st.subheader("Quarterly Sales & Net Profit Trend")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=quarterly["quarter_end"], y=quarterly["sales_cr"],
                           name="Sales (Cr)", marker_color="#6F4E37"))
    fig1.add_trace(go.Scatter(x=quarterly["quarter_end"], y=quarterly["net_profit_cr"],
                               name="Net Profit (Cr)", mode="lines+markers",
                               yaxis="y2", line=dict(color="#C9A66B", width=3)))
    fig1.update_layout(
        yaxis=dict(title="Sales (₹ Cr)"),
        yaxis2=dict(title="Net Profit (₹ Cr)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1), height=420
    )
    st.plotly_chart(fig1, use_container_width=True)

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Operating Margin (OPM%) Trend")
        fig2 = px.line(quarterly, x="quarter_end", y="opm_pct", markers=True,
                        color_discrete_sequence=["#6F4E37"])
        fig2.update_layout(yaxis_title="OPM %", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with colB:
        st.subheader("Annual Sales vs Expenses")
        annual_plot = annual[annual["year_label"] != "TTM"]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=annual_plot["year_label"], y=annual_plot["sales_cr"],
                               name="Sales", marker_color="#6F4E37"))
        fig3.add_trace(go.Bar(x=annual_plot["year_label"], y=annual_plot["expenses_cr"],
                               name="Expenses", marker_color="#C9A66B"))
        fig3.update_layout(barmode="group", height=350, yaxis_title="₹ Cr")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Raw Quarterly Data")
    st.dataframe(quarterly, use_container_width=True)

with tab2:
    st.subheader("Reserves vs Borrowings (₹ Cr)")
    bal_years = balance["fiscal_year_end"].astype(str)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=bal_years, y=balance["reserves_cr"],
                           name="Reserves", marker_color="#3A6351"))
    fig4.add_trace(go.Bar(x=bal_years, y=balance["borrowings_cr"],
                           name="Borrowings", marker_color="#B33951"))
    fig4.update_layout(barmode="group", height=400, yaxis_title="₹ Cr")
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Free Cash Flow Trend")
    fig5 = px.bar(cashflow, x=cashflow["fiscal_year_end"].astype(str), y="free_cash_flow_cr",
                  color="free_cash_flow_cr", color_continuous_scale="RdYlGn",
                  labels={"x": "Year", "free_cash_flow_cr": "Free Cash Flow (₹ Cr)"})
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)

    col_b1, col_b2 = st.columns(2)
    col_b1.dataframe(balance, use_container_width=True)
    col_b2.dataframe(cashflow, use_container_width=True)

with tab3:
    st.subheader("Cash Conversion Cycle & Working Capital Days")
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=ratios["fiscal_year_end"].astype(str),
                               y=ratios["cash_conversion_cycle"],
                               name="Cash Conversion Cycle", mode="lines+markers"))
    fig6.add_trace(go.Scatter(x=ratios["fiscal_year_end"].astype(str),
                               y=ratios["working_capital_days"],
                               name="Working Capital Days", mode="lines+markers"))
    fig6.update_layout(height=400, yaxis_title="Days")
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("ROCE % Trend")
    fig7 = px.area(ratios, x=ratios["fiscal_year_end"].astype(str), y="roce_pct",
                    color_discrete_sequence=["#6F4E37"])
    fig7.update_layout(height=350, yaxis_title="ROCE %")
    st.plotly_chart(fig7, use_container_width=True)

    st.dataframe(ratios, use_container_width=True)

with tab4:
    st.subheader("Promoter vs Institutional vs Public Holding (%)")
    share_long = shareholding.melt(
        id_vars=["quarter_end"],
        value_vars=["promoters_pct", "fii_pct", "dii_pct", "public_pct"],
        var_name="category", value_name="percentage"
    )
    fig8 = px.area(share_long, x="quarter_end", y="percentage", color="category")
    fig8.update_layout(height=420)
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Number of Shareholders Growth")
    fig9 = px.bar(shareholding, x="quarter_end", y="num_shareholders",
                  color_discrete_sequence=["#6F4E37"])
    fig9.update_layout(height=350)
    st.plotly_chart(fig9, use_container_width=True)

    st.dataframe(shareholding, use_container_width=True)

with tab5:
    st.subheader("ROCE % Comparison Across Peers")
    fig10 = px.bar(peers, x="company_name", y="roce_pct",
                   color="roce_pct", color_continuous_scale="RdYlGn",
                   labels={"company_name": "Company", "roce_pct": "ROCE %"})
    fig10.update_layout(height=420)
    st.plotly_chart(fig10, use_container_width=True)

    st.subheader("Market Cap vs P/E Ratio (bubble size = |Net Profit|)")
    peers_clean = peers.dropna(subset=["pe_ratio"]).copy()
    peers_clean["bubble_size"] = peers_clean["net_profit_qtr_cr"].abs().clip(lower=1)
    fig11 = px.scatter(peers_clean, x="pe_ratio", y="market_cap_cr",
                       size="bubble_size", color="company_name",
                       hover_data={"net_profit_qtr_cr": True, "bubble_size": False},
                       labels={"pe_ratio": "P/E Ratio", "market_cap_cr": "Market Cap (₹ Cr)"})
    fig11.update_layout(height=420)
    st.plotly_chart(fig11, use_container_width=True)

    st.dataframe(peers, use_container_width=True)

st.divider()
st.subheader("📌 Key Business Insights")
st.markdown("""
- **Revenue growth**: Quarterly sales rose from ₹21 Cr (Jun 2023) to ₹161 Cr (Jun 2026).
- **Margins**: Operating margin has stayed largely in the 16–20% band despite rapid scaling.
- **Working capital**: Cash conversion cycle improved sharply (921 days → 178 days over FY22–FY26).
- **Ownership shift**: Promoter holding declined from ~47% to ~35%, while institutional
  (FII+DII) participation rose from near-zero to ~15%.
- **Peer standing**: Vintage Coffee's ROCE (18.2%) is competitive against larger FMCG peers.
""")
