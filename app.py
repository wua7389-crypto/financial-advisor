import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="PnLytics",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# 自定义样式
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .green-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    .status-green { color: #27ae60; font-weight: bold; font-size: 1.2rem; }
    .status-yellow { color: #f39c12; font-weight: bold; font-size: 1.2rem; }
    .status-red { color: #e74c3c; font-weight: bold; font-size: 1.2rem; }
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 标题
# ============================================================
st.markdown('<div class="main-header">AI Financial Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your financial data. Get instant insights. Make smarter decisions.</div>', unsafe_allow_html=True)

# ============================================================
# 生成示例数据的函数
# ============================================================
def create_sample_data():
    data = {
        'Month': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        'Revenue': [12000,11500,13200,14800,16500,18200,19000,18500,15800,14200,13500,17800],
        'COGS': [4800,4600,5280,5920,6600,7280,7600,7400,6320,5680,5400,7120],
        'Rent': [3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,3000,3000],
        'Wages': [4000,4000,4000,4500,5000,5500,5500,5500,4500,4000,4000,5000],
        'Utilities': [500,480,520,550,600,700,750,720,600,550,500,580],
        'Marketing': [200,150,300,500,800,1000,800,600,400,300,200,500],
        'Other_Expenses': [300,250,280,320,350,400,380,360,300,280,250,350]
    }
    return pd.DataFrame(data)

def get_sample_excel():
    df = create_sample_data()
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

# ============================================================
# 分析函数
# ============================================================
def analyze(df):
    # 自动检测列名：找到Revenue列和各种费用列
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    
    # 尝试识别Revenue列
    rev_col = None
    for col in df.columns:
        if 'revenue' in col.lower() or 'sales' in col.lower() or 'income' in col.lower() or '收入' in col:
            rev_col = col
            break
    if rev_col is None and len(numeric_cols) > 0:
        rev_col = numeric_cols[0]
    
    # 尝试识别COGS列
    cogs_col = None
    for col in df.columns:
        if 'cogs' in col.lower() or 'cost of goods' in col.lower() or '成本' in col:
            cogs_col = col
            break
    
    # 找出所有费用列（除了Revenue）
    expense_cols = [c for c in numeric_cols if c != rev_col]
    
    total_revenue = df[rev_col].sum()
    total_expenses = df[expense_cols].sum().sum()
    net_profit = total_revenue - total_expenses
    
    if cogs_col:
        gross_margin = ((total_revenue - df[cogs_col].sum()) / total_revenue) * 100
    else:
        gross_margin = ((total_revenue - total_expenses) / total_revenue) * 100
    
    net_margin = (net_profit / total_revenue) * 100
    
    # 增长率
    first_rev = df[rev_col].iloc[0]
    last_rev = df[rev_col].iloc[-1]
    growth = ((last_rev - first_rev) / first_rev) * 100 if first_rev != 0 else 0
    
    # 月度利润
    df['_total_expenses'] = df[expense_cols].sum(axis=1)
    df['_net_profit'] = df[rev_col] - df['_total_expenses']
    
    best_idx = df['_net_profit'].idxmax()
    worst_idx = df['_net_profit'].idxmin()
    
    # 月份标签
    month_col = None
    for col in df.columns:
        if 'month' in col.lower() or '月' in col:
            month_col = col
            break
    if month_col is None:
        non_numeric = df.select_dtypes(exclude='number').columns.tolist()
        month_col = non_numeric[0] if non_numeric else None
    
    if month_col:
        best_month = df.loc[best_idx, month_col]
        worst_month = df.loc[worst_idx, month_col]
    else:
        best_month = f"Row {best_idx + 1}"
        worst_month = f"Row {worst_idx + 1}"
    
    # 费用分解
    cost_breakdown = {}
    for col in expense_cols:
        cost_breakdown[col] = df[col].sum()
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'gross_margin': gross_margin,
        'net_margin': net_margin,
        'growth': growth,
        'best_month': best_month,
        'best_profit': df.loc[best_idx, '_net_profit'],
        'worst_month': worst_month,
        'worst_profit': df.loc[worst_idx, '_net_profit'],
        'cost_breakdown': cost_breakdown,
        'rev_col': rev_col,
        'month_col': month_col,
        'expense_cols': expense_cols,
        'df': df
    }

def health_status(value, good, warning):
    if value >= good:
        return "🟢 Healthy", "status-green"
    elif value >= warning:
        return "🟡 Caution", "status-yellow"
    else:
        return "🔴 At Risk", "status-red"

# ============================================================
# 侧边栏：上传区域
# ============================================================
with st.sidebar:
    st.markdown("## 📁 Upload Data")
    st.markdown("Upload an Excel file with your monthly financial data.")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls', 'csv'],
        help="Your file should have columns like: Month, Revenue, COGS, Rent, Wages, etc."
    )
    
    st.markdown("---")
    st.markdown("### 🧪 No data? Try our demo!")
    
    sample_data = get_sample_excel()
    st.download_button(
        label="📥 Download Sample Data",
        data=sample_data,
        file_name="sample_boba_shop.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    use_demo = st.button("🚀 Run Demo Analysis", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("**PnLytics**")
    st.markdown("PnLytics Analytics")
    st.markdown("Turns complex financial data into actionable insights for smaill business owners.")

# ============================================================
# 主页面逻辑
# ============================================================
df = None

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully! ({len(df)} rows detected)")
elif use_demo:
    df = create_sample_data()
    st.info("📊 Running demo analysis with sample boba shop data...")

if df is not None:
    # 显示原始数据预览
    with st.expander("📋 View Raw Data", expanded=False):
        st.dataframe(df, use_container_width=True)
    
    # 运行分析
    r = analyze(df)
    
    st.markdown("---")
    
    # ============================================================
    # 第一行：核心指标卡片
    # ============================================================
    st.markdown("## 📌 Key Metrics at a Glance")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"${r['total_revenue']:,.0f}",
            delta=f"{r['growth']:+.1f}% growth" if r['growth'] >= 0 else f"{r['growth']:.1f}% decline"
        )
    with col2:
        st.metric(
            label="Total Expenses",
            value=f"${r['total_expenses']:,.0f}"
        )
    with col3:
        st.metric(
            label="Net Profit",
            value=f"${r['net_profit']:,.0f}",
            delta=f"{r['net_margin']:.1f}% margin"
        )
    
    st.markdown("")
    
    # ============================================================
    # 第二行：健康检查红绿灯
    # ============================================================
    st.markdown("## 🏥 Health Check")
    
    col1, col2, col3 = st.columns(3)
    
    gm_status, gm_class = health_status(r['gross_margin'], 50, 30)
    nm_status, nm_class = health_status(r['net_margin'], 15, 5)
    gr_status, gr_class = health_status(r['growth'], 20, 0)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Gross Margin</h3>
            <h1>{r['gross_margin']:.1f}%</h1>
            <p class="{gm_class}">{gm_status}</p>
            <p style="color:#888; font-size:0.85rem;">Is your product profitable?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Net Margin</h3>
            <h1>{r['net_margin']:.1f}%</h1>
            <p class="{nm_class}">{nm_status}</p>
            <p style="color:#888; font-size:0.85rem;">How much do you actually keep?</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Revenue Growth</h3>
            <h1>{r['growth']:.1f}%</h1>
            <p class="{gr_class}">{gr_status}</p>
            <p style="color:#888; font-size:0.85rem;">Is your business growing?</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ============================================================
    # 第三行：亮点与风险
    # ============================================================
    st.markdown("## 🌟 Highlights & Risks")
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Best Month:** {r['best_month']} — Net Profit ${r['best_profit']:,.0f}")
    with col2:
        st.error(f"**Worst Month:** {r['worst_month']} — Net Profit ${r['worst_profit']:,.0f}")
    
    st.markdown("")
    
    # ============================================================
    # 第四行：图表
    # ============================================================
    st.markdown("## 📈 Visual Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Trend", "Cost Breakdown", "Monthly Profit"])
    
    with tab1:
        month_col = r['month_col']
        rev_col = r['rev_col']
        chart_df = r['df']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df[month_col] if month_col else chart_df.index,
            y=chart_df[rev_col],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=chart_df[month_col] if month_col else chart_df.index,
            y=chart_df['_net_profit'],
            mode='lines+markers',
            name='Net Profit',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(76,175,80,0.15)'
        ))
        fig.update_layout(
            title='Monthly Revenue vs Net Profit',
            xaxis_title='Month',
            yaxis_title='Amount ($)',
            template='plotly_white',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        cost_df = pd.DataFrame({
            'Category': list(r['cost_breakdown'].keys()),
            'Amount': list(r['cost_breakdown'].values())
        })
        fig2 = px.pie(
            cost_df,
            values='Amount',
            names='Category',
            title='Where Does Your Money Go?',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig2.update_layout(height=450)
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        fig3 = go.Figure()
        colors = ['#4CAF50' if v >= 0 else '#e74c3c' for v in chart_df['_net_profit']]
        fig3.add_trace(go.Bar(
            x=chart_df[month_col] if month_col else chart_df.index,
            y=chart_df['_net_profit'],
            marker_color=colors,
            name='Net Profit'
        ))
        fig3.update_layout(
            title='Monthly Net Profit (Green = Profit, Red = Loss)',
            xaxis_title='Month',
            yaxis_title='Net Profit ($)',
            template='plotly_white',
            height=450
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # ============================================================
    # 第五行：AI建议（简单版）
    # ============================================================
    st.markdown("## 💡 AI Recommendations")
    
    recommendations = []
    
    if r['net_margin'] < 5:
        recommendations.append("⚠️ **Your net margin is dangerously low.** You're keeping less than 5 cents for every dollar earned. Consider cutting your largest expense category or raising prices by 10-15%.")
    elif r['net_margin'] < 15:
        recommendations.append("🟡 **Your net margin is okay but could be better.** Industry average for small businesses is 10-15%. Look for ways to reduce overhead costs.")
    else:
        recommendations.append("🟢 **Your net margin is healthy!** You're running an efficient operation. Focus on growth while maintaining this margin.")
    
    if r['growth'] < 0:
        recommendations.append("📉 **Revenue is declining.** This is a red flag. Consider investing more in marketing or exploring new revenue streams.")
    elif r['growth'] > 30:
        recommendations.append("🚀 **Impressive growth!** Make sure your operations can scale. Rapid growth without infrastructure can lead to quality issues.")
    
    # 找最大费用
    biggest_cost = max(r['cost_breakdown'].items(), key=lambda x: x[1])
    cost_pct = (biggest_cost[1] / r['total_expenses']) * 100
    recommendations.append(f"💰 **Your biggest expense is {biggest_cost[0]}** at ${biggest_cost[1]:,.0f} ({cost_pct:.0f}% of total costs). This is your #1 lever for improving profitability.")
    
    for rec in recommendations:
        st.markdown(rec)
    
    st.markdown("---")
    st.markdown("*Report generated by AI Financial Advisor v2.0 | Built by Alex Wu*")

else:
    # 没有上传文件时的欢迎页面
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 📤 Upload
        Drop your Excel file with monthly revenue and expense data.
        """)
    with col2:
        st.markdown("""
        ### ⚡ Analyze
        Our engine calculates 6+ key financial metrics instantly.
        """)
    with col3:
        st.markdown("""
        ### 📊 Insights
        Get visual reports, health checks, and AI recommendations.
        """)
    
    st.markdown("---")
    st.markdown("### 👈 Get started by uploading a file in the sidebar, or click 'Run Demo Analysis' to see it in action!")
