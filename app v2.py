import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="Abacus",
    page_icon="◧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Custom CSS — White + Indigo accent, clean & intellectual
# ============================================================
INDIGO = "#3F51B5"
INDIGO_DARK = "#283593"
INDIGO_LIGHT = "#C5CAE9"
INDIGO_BG = "#E8EAF6"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+4:wght@400;600&display=swap');

    .stApp {{
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #f8f9fc;
        border-right: 1px solid #e8eaf0;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown label {{
        color: #555;
        font-size: 0.88rem;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #222;
    }}

    h1 {{
        font-family: 'Source Serif 4', serif !important;
        font-weight: 600 !important;
        color: #1a1a2e !important;
        letter-spacing: -0.02em;
    }}
    h2, h3 {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: #222 !important;
    }}

    div[data-testid="stMetric"] {{
        background-color: #ffffff;
        border: 1px solid #e0e3eb;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 1px 3px rgba(63,81,181,0.04);
    }}
    div[data-testid="stMetric"] label {{
        color: #7986CB !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: #1a1a2e !important;
        font-weight: 600 !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px;
        border-bottom: 1px solid #e0e3eb;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #9e9e9e;
        padding: 10px 24px;
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        color: {INDIGO} !important;
        border-bottom: 2px solid {INDIGO} !important;
    }}

    hr {{
        border: none;
        border-top: 1px solid #e8eaf0;
        margin: 2rem 0;
    }}

    .footer-text {{
        text-align: center;
        color: #b0b0b0;
        font-size: 0.75rem;
        padding: 2rem 0 1rem 0;
        letter-spacing: 0.04em;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    .stButton > button {{
        background-color: {INDIGO};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 0.5rem 1.5rem;
        letter-spacing: 0.02em;
    }}
    .stButton > button:hover {{
        background-color: {INDIGO_DARK};
        color: #ffffff;
    }}

    .stDataFrame {{
        border: 1px solid #e0e3eb;
        border-radius: 10px;
    }}

    .stDownloadButton > button {{
        background-color: #ffffff;
        color: {INDIGO};
        border: 1px solid {INDIGO};
        border-radius: 8px;
        font-weight: 500;
    }}
    .stDownloadButton > button:hover {{
        background-color: {INDIGO_BG};
        color: {INDIGO_DARK};
    }}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663291964821/QjDLltQWooriJzwW.png"

# ============================================================
# Helper Functions
# ============================================================

def traffic_light(value, good_threshold, bad_threshold, higher_is_better=True):
    if higher_is_better:
        if value >= good_threshold:
            return "Healthy", "#2E7D32"
        elif value >= bad_threshold:
            return "Caution", "#F57F17"
        else:
            return "At Risk", "#C62828"
    else:
        if value <= good_threshold:
            return "Healthy", "#2E7D32"
        elif value <= bad_threshold:
            return "Caution", "#F57F17"
        else:
            return "At Risk", "#C62828"


def generate_insights(results):
    insights = []
    nm = results['net_margin']
    gm = results['gross_margin']
    growth = results['revenue_growth']

    if nm > 15:
        insights.append("Strong net margin indicates efficient cost management. Consider reinvesting surplus into growth channels.")
    elif nm > 5:
        insights.append("Net margin is moderate. Review your largest expense categories for potential optimization.")
    else:
        insights.append("Net margin is thin. Immediate attention needed on cost structure \u2014 identify and reduce non-essential spending.")

    if gm > 60:
        insights.append("Gross margin is healthy, suggesting good pricing power or low direct costs.")
    elif gm < 40:
        insights.append("Gross margin is below average. Evaluate supplier contracts and consider renegotiating terms or finding alternatives.")

    if growth > 30:
        insights.append("Revenue growth is strong. Ensure operational capacity can sustain this pace \u2014 watch for cash flow strain during rapid expansion.")
    elif growth > 0:
        insights.append("Steady growth trajectory. Look for opportunities to accelerate through targeted marketing or expanding service offerings.")
    else:
        insights.append("Revenue is declining. Prioritize customer retention and investigate root causes \u2014 market shift, competition, or seasonal factors.")

    sorted_costs = sorted(results['cost_breakdown'].items(), key=lambda x: x[1], reverse=True)
    top_cost = sorted_costs[0]
    pct = (top_cost[1] / results['total_expenses']) * 100
    if pct > 35:
        insights.append(f"Your largest cost driver is {top_cost[0]} at {pct:.0f}% of total expenses. High concentration in one category increases vulnerability.")

    best = results['best_month']
    worst = results['worst_month']
    insights.append(f"Peak profitability occurs in {best}. Consider aligning major initiatives and inventory buildup ahead of this period. {worst} is your weakest month \u2014 plan reserves accordingly.")

    return insights


def calculate_metrics(df):
    rev_col = None
    for col in df.columns:
        if any(k in col.lower() for k in ['revenue', 'sales', 'income']):
            rev_col = col
            break
    if rev_col is None:
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            rev_col = numeric_cols[0]

    month_col = None
    for col in df.columns:
        if 'month' in col.lower():
            month_col = col
            break
    if month_col is None:
        non_numeric = df.select_dtypes(exclude='number').columns.tolist()
        month_col = non_numeric[0] if non_numeric else None

    cogs_col = None
    for col in df.columns:
        if any(k in col.upper() for k in ['COGS', 'COST_OF_GOODS', 'COST OF GOODS', 'DIRECT_COST']):
            cogs_col = col
            break

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    expense_cols = [c for c in numeric_cols if c != rev_col]

    df['Total_Expenses'] = df[expense_cols].sum(axis=1)
    df['Net_Profit'] = df[rev_col] - df['Total_Expenses']
    df['Profit_Margin'] = (df['Net_Profit'] / df[rev_col] * 100).round(1)

    total_rev = df[rev_col].sum()
    total_exp = df['Total_Expenses'].sum()
    total_profit = total_rev - total_exp

    if cogs_col:
        gross_margin = ((total_rev - df[cogs_col].sum()) / total_rev) * 100
    else:
        gross_margin = ((total_rev - total_exp) / total_rev) * 100

    net_margin = (total_profit / total_rev) * 100
    revenue_growth = ((df[rev_col].iloc[-1] - df[rev_col].iloc[0]) / df[rev_col].iloc[0]) * 100 if df[rev_col].iloc[0] != 0 else 0

    best_idx = df['Net_Profit'].idxmax()
    worst_idx = df['Net_Profit'].idxmin()

    cost_breakdown = {}
    for col in expense_cols:
        cost_breakdown[col] = df[col].sum()

    avg_monthly_profit = df['Net_Profit'].mean()
    months_profitable = (df['Net_Profit'] > 0).sum()

    return {
        'monthly_data': df,
        'rev_col': rev_col,
        'month_col': month_col,
        'total_revenue': total_rev,
        'total_expenses': total_exp,
        'total_profit': total_profit,
        'gross_margin': gross_margin,
        'net_margin': net_margin,
        'revenue_growth': revenue_growth,
        'best_month': df.loc[best_idx, month_col] if month_col else f"Row {best_idx+1}",
        'best_profit': df.loc[best_idx, 'Net_Profit'],
        'worst_month': df.loc[worst_idx, month_col] if month_col else f"Row {worst_idx+1}",
        'worst_profit': df.loc[worst_idx, 'Net_Profit'],
        'cost_breakdown': cost_breakdown,
        'avg_monthly_profit': avg_monthly_profit,
        'months_profitable': months_profitable,
        'total_months': len(df)
    }


def create_demo_data():
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'Revenue': [12000, 11500, 13200, 14800, 16500, 18200,
                    19000, 18500, 15800, 14200, 13500, 17800],
        'COGS': [4800, 4600, 5280, 5920, 6600, 7280,
                 7600, 7400, 6320, 5680, 5400, 7120],
        'Rent': [3000, 3000, 3000, 3000, 3000, 3000,
                 3000, 3000, 3000, 3000, 3000, 3000],
        'Wages': [4000, 4000, 4000, 4500, 5000, 5500,
                  5500, 5500, 4500, 4000, 4000, 5000],
        'Utilities': [500, 480, 520, 550, 600, 700,
                      750, 720, 600, 550, 500, 580],
        'Marketing': [200, 150, 300, 500, 800, 1000,
                      800, 600, 400, 300, 200, 500],
        'Other': [300, 250, 280, 320, 350, 400,
                  380, 360, 300, 280, 250, 350]
    }
    return pd.DataFrame(data)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; padding:8px 0 16px 0;">'
        f'<img src="{LOGO_URL}" style="width:40px; height:40px; border-radius:10px;">'
        f'<span style="font-family:Source Serif 4,serif; font-size:1.3rem; font-weight:600; color:#1a1a2e;">Abacus</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p style="color:#888; font-size:0.8rem; margin-top:-8px;">Financial clarity, simplified.</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("##### Data Source")
    data_source = st.radio(
        "Choose input method",
        ["Upload File", "Demo Data"],
        label_visibility="collapsed"
    )

    df = None

    if data_source == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload your financial data",
            type=['xlsx', 'xls', 'csv'],
            help="Excel or CSV with columns: Month, Revenue, and expense categories"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.success(f"Loaded {len(df)} rows")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        df = create_demo_data()
        st.markdown(
            f'<p style="color:{INDIGO}; font-size:0.82rem;">Using sample data</p>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        '<p style="color:#999; font-size:0.72rem; line-height:1.5;">'
        'Upload monthly revenue and expense data. '
        'Abacus generates a diagnostic report with actionable insights.'
        '</p>',
        unsafe_allow_html=True
    )


# ============================================================
# Main Content
# ============================================================

if df is None:
    st.markdown("")
    st.markdown("")

    col_l, col_c, col_r = st.columns([1, 3, 1])
    with col_c:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:16px; margin-bottom:8px;">'
            f'<img src="{LOGO_URL}" style="width:52px; height:52px; border-radius:12px;">'
            f'<h1 style="margin:0; font-size:2.4rem;">Abacus</h1>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p style="color:#666; font-size:1.1rem; line-height:1.7; max-width:520px;">'
            'Upload your financial data. Get a clear diagnostic in seconds. '
            'No jargon, no complexity \u2014 just the numbers that matter.'
            '</p>',
            unsafe_allow_html=True
        )
        st.markdown("")
        st.markdown(
            f'<p style="color:#999; font-size:0.85rem;">'
            'Use the sidebar to upload an Excel or CSV file, or select Demo Data to explore.'
            '</p>',
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.markdown("##### How it works")
        st.markdown(
            f'<p style="color:#555; font-size:0.9rem; line-height:1.8;">'
            f'<strong style="color:{INDIGO};">1.</strong> Upload a spreadsheet with monthly revenue and expenses.<br>'
            f'<strong style="color:{INDIGO};">2.</strong> Abacus calculates margins, trends, and risk indicators.<br>'
            f'<strong style="color:{INDIGO};">3.</strong> Read your diagnostic report and act on the insights.'
            f'</p>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(
            '<p class="footer-text">Abacus \u2014 clarity over complexity</p>',
            unsafe_allow_html=True
        )

else:
    results = calculate_metrics(df)
    m = results['monthly_data']
    rev_col = results['rev_col']
    month_col = results['month_col']

    # Header
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">'
        f'<img src="{LOGO_URL}" style="width:36px; height:36px; border-radius:8px;">'
        f'<h1 style="margin:0; font-size:1.8rem;">Abacus</h1>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="color:#7986CB; font-size:0.85rem; margin-top:-4px;">Financial Diagnostic Report</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ---- Key Metrics ----
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Revenue", f"${results['total_revenue']:,.0f}")
    c2.metric("Expenses", f"${results['total_expenses']:,.0f}")
    c3.metric("Net Profit", f"${results['total_profit']:,.0f}")
    c4.metric("Net Margin", f"{results['net_margin']:.1f}%")
    c5.metric("Growth", f"{results['revenue_growth']:.1f}%")

    st.markdown("")

    # ---- Health Check ----
    st.markdown("##### Health Check")
    h1, h2, h3, h4 = st.columns(4)

    checks = [
        ("Gross Margin", results['gross_margin'], 50, 30, True),
        ("Net Margin", results['net_margin'], 10, 5, True),
        ("Revenue Growth", results['revenue_growth'], 20, 0, True),
        ("Profitable Months", (results['months_profitable']/results['total_months'])*100, 80, 50, True),
    ]

    for col, (label, val, good, bad, higher) in zip([h1, h2, h3, h4], checks):
        status, color = traffic_light(val, good, bad, higher)
        col.markdown(
            f'<div style="background:#ffffff; border:1px solid #e0e3eb; border-radius:10px; padding:16px 20px; box-shadow:0 1px 3px rgba(63,81,181,0.04);">'
            f'<p style="color:#7986CB; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em; margin:0;">{label}</p>'
            f'<p style="color:{color}; font-size:0.95rem; font-weight:600; margin:4px 0 0 0;">{status}</p>'
            f'<p style="color:#bbb; font-size:0.75rem; margin:2px 0 0 0;">{val:.1f}%</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("")

    # ---- Tabs ----
    tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Cost Structure", "Data", "Insights"])

    with tab1:
        st.markdown("")

        x_axis = m[month_col] if month_col else m.index

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=x_axis, y=m[rev_col],
            name='Revenue',
            line=dict(color=INDIGO, width=2.5),
            mode='lines+markers',
            marker=dict(size=5)
        ))
        fig1.add_trace(go.Scatter(
            x=x_axis, y=m['Net_Profit'],
            name='Net Profit',
            line=dict(color='#2E7D32', width=2),
            mode='lines+markers',
            marker=dict(size=5),
            fill='tozeroy',
            fillcolor='rgba(46,125,50,0.06)'
        ))
        fig1.update_layout(
            title=dict(text='Revenue vs Net Profit', font=dict(size=14, color='#333')),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(family='Inter', size=12, color='#666'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis=dict(gridcolor='#f0f0f0', title='Month'),
            yaxis=dict(gridcolor='#f0f0f0', tickprefix='$', title='Amount'),
            height=380
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=x_axis, y=m['Profit_Margin'],
            marker_color=[INDIGO if v > 0 else '#C62828' for v in m['Profit_Margin']],
            opacity=0.85
        ))
        fig2.update_layout(
            title=dict(text='Monthly Profit Margin', font=dict(size=14, color='#333')),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(family='Inter', size=12, color='#666'),
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis=dict(gridcolor='#f0f0f0', title='Month'),
            yaxis=dict(gridcolor='#f0f0f0', ticksuffix='%', title='Profit Margin'),
            height=280,
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("")

        col_pie, col_table = st.columns([1, 1])

        with col_pie:
            labels = list(results['cost_breakdown'].keys())
            values = list(results['cost_breakdown'].values())
            colors = [INDIGO, '#5C6BC0', '#7986CB', '#9FA8DA', INDIGO_LIGHT, '#E8EAF6', '#F5F5F5']

            fig3 = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors[:len(labels)]),
                textinfo='label+percent',
                textfont=dict(size=11, family='Inter'),
                hovertemplate='%{label}: $%{value:,.0f}<extra></extra>'
            )])
            fig3.update_layout(
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font=dict(family='Inter', size=12, color='#555'),
                margin=dict(l=10, r=10, t=10, b=10),
                height=360,
                showlegend=False
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col_table:
            sorted_costs = sorted(results['cost_breakdown'].items(), key=lambda x: x[1], reverse=True)
            cost_df = pd.DataFrame(sorted_costs, columns=['Category', 'Amount'])
            cost_df['Share'] = (cost_df['Amount'] / cost_df['Amount'].sum() * 100).round(1)
            cost_df['Amount'] = cost_df['Amount'].apply(lambda x: f"${x:,.0f}")
            cost_df['Share'] = cost_df['Share'].apply(lambda x: f"{x}%")
            st.dataframe(cost_df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("")
        display_cols = [c for c in m.columns if c not in ['Total_Expenses', 'Net_Profit', 'Profit_Margin']]
        display_df = m[display_cols].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        output = BytesIO()
        m.to_excel(output, index=False)
        output.seek(0)
        st.download_button(
            label="Download Full Report",
            data=output,
            file_name="abacus_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab4:
        st.markdown("")
        insights = generate_insights(results)

        for i, insight in enumerate(insights, 1):
            st.markdown(
                f'<div style="background:#ffffff; border-left:3px solid {INDIGO}; padding:14px 18px; margin-bottom:12px; border-radius:0 8px 8px 0; box-shadow:0 1px 3px rgba(63,81,181,0.04);">'
                f'<p style="color:#333; font-size:0.88rem; line-height:1.65; margin:0;">{insight}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("")
        st.markdown(
            '<p style="color:#bbb; font-size:0.75rem;">'
            'These insights are generated based on standard financial benchmarks. '
            'They are not a substitute for professional financial advice.'
            '</p>',
            unsafe_allow_html=True
        )

    # ---- Summary Bar ----
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown(
        f'<p style="color:#7986CB; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em;">Best Month</p>'
        f'<p style="color:#1a1a2e; font-size:1rem; font-weight:600;">{results["best_month"]}</p>'
        f'<p style="color:#2E7D32; font-size:0.8rem;">${results["best_profit"]:,.0f} profit</p>',
        unsafe_allow_html=True
    )
    s2.markdown(
        f'<p style="color:#7986CB; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em;">Worst Month</p>'
        f'<p style="color:#1a1a2e; font-size:1rem; font-weight:600;">{results["worst_month"]}</p>'
        f'<p style="color:#C62828; font-size:0.8rem;">${results["worst_profit"]:,.0f} profit</p>',
        unsafe_allow_html=True
    )
    s3.markdown(
        f'<p style="color:#7986CB; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em;">Avg Monthly Profit</p>'
        f'<p style="color:#1a1a2e; font-size:1rem; font-weight:600;">${results["avg_monthly_profit"]:,.0f}</p>',
        unsafe_allow_html=True
    )
    s4.markdown(
        f'<p style="color:#7986CB; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em;">Gross Margin</p>'
        f'<p style="color:#1a1a2e; font-size:1rem; font-weight:600;">{results["gross_margin"]:.1f}%</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="footer-text">Abacus \u2014 clarity over complexity</p>',
        unsafe_allow_html=True
    )
