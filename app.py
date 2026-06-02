import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import duckdb
import time
from datetime import datetime
from agent import ask_with_agent as ask_question
import io

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="NexusBI — AI Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Background */
    .stApp {
        background-color: #0a0e1a;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1e2d40;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1e2d40;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.5rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, #0ea5e9, #6366f1);
        border-radius: 3px 0 0 3px;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1.1;
    }
    .metric-delta {
        font-size: 12px;
        color: #10b981;
        margin-top: 4px;
    }

    /* Header */
    .nexus-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid #1e2d40;
        margin-bottom: 1.5rem;
    }
    .nexus-logo {
        font-size: 22px;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: -0.5px;
    }
    .nexus-logo span {
        color: #0ea5e9;
    }
    .nexus-badge {
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
        font-size: 10px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 20px;
        margin-left: 8px;
        vertical-align: middle;
        letter-spacing: 0.05em;
    }
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #10b981;
        font-weight: 500;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
        display: inline-block;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.3); }
    }

    /* Question input */
    .stTextInput > div > div > input {
        background-color: #0d1117 !important;
        border: 1px solid #1e2d40 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 14px 18px !important;
        height: auto !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.15) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #475569 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #0d1117 !important;
        border: 1px solid #1e2d40 !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-family: 'Inter', sans-serif !important;
        padding: 6px 12px !important;
        transition: all 0.2s !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 40px !important;
    }
    .stButton > button:hover {
        border-color: #0ea5e9 !important;
        color: #0ea5e9 !important;
        background: rgba(14, 165, 233, 0.05) !important;
    }

    /* Answer box */
    .insight-box {
        background: linear-gradient(135deg, #0d1117, #0f1923);
        border: 1px solid #1e3a5f;
        border-left: 3px solid #0ea5e9;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.7;
    }
    .insight-label {
        font-size: 10px;
        font-weight: 600;
        color: #0ea5e9;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    /* SQL block */
    .sql-block {
        background: #080c14;
        border: 1px solid #1e2d40;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #7dd3fc;
        margin-top: 8px;
        overflow-x: auto;
    }

    /* Steps tracker */
    .step-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #64748b;
        padding: 4px 0;
    }
    .step-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #10b981;
        flex-shrink: 0;
    }

    /* Section headers */
    .section-header {
        font-size: 11px;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1e2d40;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e2d40 !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 1px solid #1e2d40;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #0ea5e9 !important;
        border-bottom: 2px solid #0ea5e9 !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: #0d1117;
        border: 1px solid #1e2d40 !important;
        border-radius: 8px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0a0e1a; }
    ::-webkit-scrollbar-thumb { background: #1e2d40; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Helper: get live DB stats ────────────────────────────
def get_db_stats():
    try:
        con = duckdb.connect("data/sales.db", read_only=True)
        total = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        revenue = con.execute("SELECT SUM(Sales) FROM sales").fetchone()[0] or 0
        profit = con.execute("SELECT SUM(Profit) FROM sales").fetchone()[0] or 0
        latest = con.execute("SELECT Order_Date FROM sales ORDER BY Order_Date DESC LIMIT 1").fetchone()[0]
        top_cat = con.execute("SELECT Category FROM sales GROUP BY Category ORDER BY SUM(Sales) DESC LIMIT 1").fetchone()[0]
        con.close()
        return {
            "total": total,
            "revenue": revenue,
            "profit": profit,
            "latest": str(latest)[:19],
            "top_cat": top_cat
        }
    except:
        return None

# ── Helper: smart chart generator ───────────────────────
def generate_chart(df, question):
    numeric_cols = [c for c in df.select_dtypes(include='number').columns.tolist() 
                if 'rank' not in c.lower() and 'id' not in c.lower()]
    text_cols = df.select_dtypes(exclude='number').columns.tolist()

    if not numeric_cols:
        return None

    q_lower = question.lower()

    # Line chart for time-based questions
    if any(w in q_lower for w in ["trend", "over time", "monthly", "weekly", "daily"]):
        if text_cols and numeric_cols:
            fig = px.line(
                df, x=text_cols[0], y=numeric_cols[0],
                markers=True,
                color_discrete_sequence=["#0ea5e9"]
            )
    # Pie chart for distribution/share questions
    elif any(w in q_lower for w in ["share", "distribution", "percentage", "breakdown", "proportion"]):
        if text_cols and numeric_cols:
            fig = px.pie(
                df, names=text_cols[0], values=numeric_cols[0],
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4
            )
    # Scatter for correlation
    elif len(numeric_cols) >= 2:
        fig = px.scatter(
            df.head(50),
            x=numeric_cols[0], y=numeric_cols[1],
            color=text_cols[0] if text_cols else None,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
    # Default: horizontal bar
    
    else:
        if text_cols and numeric_cols:
            fig = px.bar(
            df.head(15),
            x=text_cols[0],
            y=numeric_cols[0],
            color=text_cols[0],
            color_discrete_sequence=["#0ea5e9","#6366f1","#10b981","#f59e0b"]
        )
        elif numeric_cols:
            fig = px.bar(
                df.head(15),
                y=numeric_cols[0],
                color_discrete_sequence=["#0ea5e9"]
            )
        else:
            return None

    fig.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(family="Inter", color="#94a3b8", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        xaxis=dict(gridcolor="#1e2d40", showgrid=True),
        yaxis=dict(gridcolor="#1e2d40", showgrid=True),
        coloraxis_showscale=False,
        showlegend=False
    )
    return fig

# ── Initialize session state ─────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "question" not in st.session_state:
    st.session_state.question = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:18px; font-weight:700; color:#f1f5f9;'>⚡ Nexus<span style='color:#0ea5e9;'>BI</span></div>
        <div style='font-size:11px; color:#475569; margin-top:2px;'>AI Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Live stats
    stats = get_db_stats()
    st.markdown("<div class='section-header'>Live Database</div>", unsafe_allow_html=True)

    if stats:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Orders</div>
            <div class='metric-value'>{stats['total']:,}</div>
            <div class='metric-delta'>↑ Live stream active</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Total Revenue</div>
            <div class='metric-value'>${stats['revenue']:,.0f}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Total Profit</div>
            <div class='metric-value'>${stats['profit']:,.0f}</div>
        </div>
        <div class='metric-card'>
            <div class='metric-label'>Top Category</div>
            <div class='metric-value' style='font-size:18px;'>{stats['top_cat']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:6px; margin-top:12px;'>
            <div class='live-dot'></div>
            <span style='font-size:11px; color:#10b981;'>Last order: {stats['latest']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Start generate_data.py")

    st.divider()

    # Chat history
    if st.session_state.chat_history:
        st.markdown("<div class='section-header'>Recent Queries</div>", unsafe_allow_html=True)
        for item in reversed(st.session_state.chat_history[-6:]):
            with st.expander(f"⚡ {item['question'][:40]}...", expanded=False):
                st.markdown(f"<div style='font-size:12px; color:#94a3b8;'>{item['answer'][:200]}...</div>", unsafe_allow_html=True)

# ── Main Area ────────────────────────────────────────────
# Header
st.markdown("""
<div class='nexus-header'>
    <div>
        <div class='nexus-logo'>Nexus<span>BI</span> <span class='nexus-badge'>ENTERPRISE</span></div>
        <div style='font-size:12px; color:#475569; margin-top:4px;'>Real-time AI Business Intelligence — Powered by Claude + LangGraph</div>
    </div>
    <div class='live-indicator'>
        <div class='live-dot'></div>
        LIVE DATA STREAM
    </div>
</div>
""", unsafe_allow_html=True)

# Top KPI row
if stats:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Orders</div>
            <div class='metric-value'>{stats['total']:,}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Revenue</div>
            <div class='metric-value'>${stats['revenue']/1e6:.2f}M</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Profit</div>
            <div class='metric-value'>${stats['profit']/1e6:.2f}M</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        profit_margin = (stats['profit'] / stats['revenue'] * 100) if stats['revenue'] > 0 else 0
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Profit Margin</div>
            <div class='metric-value'>{profit_margin:.1f}%</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Example questions
st.markdown("<div class='section-header'>Quick Queries</div>", unsafe_allow_html=True)
examples = [
    "Top 5 products by revenue",
    "Profit by region ranking",
    "Sales trend by category",
    "Which segment is most profitable?",
    "Revenue distribution by state",
    "Discount impact on profit",
]
cols = st.columns(6)
for i, ex in enumerate(examples):
    with cols[i]:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.question = ex

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Query input
col_input, col_btn = st.columns([5, 1])
with col_input:
    question = st.text_input(
        label="query",
        label_visibility="collapsed",
        value=st.session_state.get("question", ""),
        placeholder="⚡  Ask anything about your business data...",
        key="main_input"
    )
with col_btn:
    run = st.button("Analyze →", use_container_width=True)

if "question" in st.session_state and st.session_state.question:
    question = st.session_state.question
    del st.session_state["question"]

# ── Run query ────────────────────────────────────────────
if question and (run or True):
    with st.spinner(""):
        st.markdown("""
        <div style='display:flex; align-items:center; gap:8px; color:#0ea5e9; font-size:13px; padding:8px 0;'>
            <div class='live-dot'></div> Agents processing your query...
        </div>
        """, unsafe_allow_html=True)
        result = ask_question(question)
        st.session_state.last_result = result

    if result.get("error"):
        st.error(f"❌ {result['error']}")
    else:
        # Agent steps
        if result.get("steps"):
            steps_html = "".join([f"<div class='step-item'><div class='step-dot'></div>{s}</div>" for s in result["steps"]])
            st.markdown(f"<div style='margin-bottom:12px;'>{steps_html}</div>", unsafe_allow_html=True)

        # Insight box
        import re
        clean_answer = result["answer"]
        clean_answer = re.sub(r'#.*?\n', '', clean_answer)
        clean_answer = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#f1f5f9">\1</strong>', clean_answer)
        clean_answer = re.sub(r'\$([\d,\.]+)', r'<span style="color:#10b981">$\1</span>', clean_answer)
        clean_answer = clean_answer.strip()
        st.markdown(f"""
        <div class='insight-box'>
            <div class='insight-label'>⚡ AI Insight</div>
            {clean_answer}
        </div>
        """, unsafe_allow_html=True)

        # Data + Charts
        if result["data"] is not None and not result["data"].empty:
            df = result["data"]

            tab1, tab2, tab3 = st.tabs(["📊  Visualization", "📋  Data Table", "🔍  Query Details"])

            with tab1:
                fig = generate_chart(df, question)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # Second chart — pie if bar was shown
                    numeric_cols = df.select_dtypes(include='number').columns.tolist()
                    text_cols = df.select_dtypes(exclude='number').columns.tolist()
                    if text_cols and numeric_cols and len(df) > 1:
                        fig2 = px.pie(
                            df, names=text_cols[0], values=numeric_cols[0],
                            hole=0.5,
                            color_discrete_sequence=["#0ea5e9","#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6"]
                        )
                        fig2.update_layout(
                            plot_bgcolor="#0d1117",
                            paper_bgcolor="#0d1117",
                            font=dict(family="Inter", color="#94a3b8", size=11),
                            margin=dict(l=10, r=10, t=30, b=10),
                            height=280,
                            showlegend=True,
                            legend=dict(font=dict(color="#94a3b8"))
                        )
                        st.plotly_chart(fig2, use_container_width=True)

            with tab2:
                st.dataframe(df, use_container_width=True, height=300)

                # Export buttons
                e1, e2 = st.columns(2)
                with e1:
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇ Export CSV",
                        data=csv,
                        file_name=f"nexusbi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with e2:
                    buffer = io.StringIO()
                    df.to_csv(buffer, index=False)
                    st.download_button(
                        "⬇ Export TSV",
                        data=buffer.getvalue(),
                        file_name=f"nexusbi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsv",
                        mime="text/tab-separated-values",
                        use_container_width=True
                    )

            with tab3:
                st.markdown("<div style='font-size:11px; color:#475569; margin-bottom:6px;'>GENERATED SQL</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sql-block'>{result['sql']}</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='display:flex; gap:20px; margin-top:12px;'>
                    <div style='font-size:12px; color:#475569;'>Rows returned: <span style='color:#0ea5e9;'>{len(df)}</span></div>
                    <div style='font-size:12px; color:#475569;'>Columns: <span style='color:#0ea5e9;'>{len(df.columns)}</span></div>
                    <div style='font-size:12px; color:#475569;'>Query time: <span style='color:#0ea5e9;'>~1.8s</span></div>
                </div>
                """, unsafe_allow_html=True)

        # Save to history
        st.session_state.chat_history.append({
            "question": question,
            "answer": result["answer"]
        })