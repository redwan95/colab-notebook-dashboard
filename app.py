"""
AI-Powered Colab Notebook Manager
Fixed Version - Works on Streamlit Cloud
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os

# Page config
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - FIXED DARK THEME (Readable)
# ============================================
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }
    
    /* All text color */
    html, body, [class*="css"] {
        color: #ffffff !important;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #58a6ff !important;
    }
    
    /* Main title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #58a6ff;
        text-align: center;
        padding: 20px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .stSidebar [data-testid="stMarkdown"] {
        color: #c9d1d9;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: #58a6ff;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-top: 5px;
    }
    
    /* Notebook cards */
    .notebook-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .notebook-title {
        color: #f0f6fc;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .notebook-info {
        color: #8b949e;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Tags */
    .tag {
        background-color: #388bfd;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 3px;
        display: inline-block;
    }
    
    .tag-category {
        background-color: #a371f7;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #c9d1d9;
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        background-color: #0d1117;
    }
    
    .stSelectbox [data-baseweb="input"] {
        background-color: #161b22;
        color: white;
    }
    
    /* Text input */
    .stTextInput input, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }
    
    /* Success/Info/Warning boxes */
    .stAlert {
        background-color: #161b22;
        border-radius: 8px;
    }
    
    /* Info box */
    .info-box {
        background-color: #161b22;
        border-left: 4px solid #58a6ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #c9d1d9;
    }
    
    /* Links */
    a {
        color: #58a6ff !important;
        text-decoration: none;
    }
    
    /* Section divider */
    .divider {
        border-top: 1px solid #30363d;
        margin: 30px 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #161b22;
        border-radius: 8px;
        color: #f0f6fc;
    }
    
    /* Dataframe */
    .dataframe {
        background-color: #161b22;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 8px;
    }
    
    /* Help text */
    .help-text {
        color: #8b949e;
        font-size: 0.9rem;
    }
    
    /* Card header */
    .card-header {
        background-color: #0d1117;
        padding: 15px;
        border-radius: 8px 8px 0 0;
        border-bottom: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================
def init_db():
    """Initialize database"""
    db_path = 'database.db'
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notebooks (
            id TEXT,
            name TEXT,
            account TEXT,
            created_time TEXT,
            modified_time TEXT,
            web_link TEXT,
            colab_link TEXT,
            size INTEGER,
            code_content TEXT,
            markdown_content TEXT,
            total_code_lines INTEGER,
            scanned_at TEXT,
            analyzed INTEGER DEFAULT 0,
            summary TEXT,
            tags TEXT,
            category TEXT,
            main_goal TEXT,
            key_findings TEXT,
            technologies TEXT,
            PRIMARY KEY (id, account)
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path


def get_db_data(db_path):
    """Get all data from database"""
    try:
        if not os.path.exists(db_path):
            return pd.DataFrame(), {}
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM notebooks ORDER BY modified_time DESC", conn)
        conn.close()
        
        # Get stats
        stats = get_stats(df)
        
        return df, stats
    except Exception as e:
        return pd.DataFrame(), {}


def get_stats(df):
    """Calculate statistics"""
    stats = {
        'total': 0,
        'analyzed': 0,
        'pending': 0,
        'lines': 0,
        'categories': {},
        'accounts': {}
    }
    
    if df.empty:
        return stats
    
    stats['total'] = len(df)
    stats['analyzed'] = len(df[df['analyzed'] == 1]) if 'analyzed' in df.columns else 0
    stats['pending'] = stats['total'] - stats['analyzed']
    stats['lines'] = df['total_code_lines'].sum() if 'total_code_lines' in df.columns else 0
    
    if 'category' in df.columns:
        cats = df['category'].value_counts().to_dict()
        stats['categories'] = {k: v for k, v in cats.items() if k}
    
    if 'account' in df.columns:
        accs = df['account'].value_counts().to_dict()
        stats['accounts'] = {k: v for k, v in accs.items() if k}
    
    return stats


def search_df(df, term):
    """Search dataframe"""
    if df.empty:
        return df
    
    term = term.lower()
    mask = (
        df['name'].str.lower().str.contains(term, na=False) |
        df['summary'].str.lower().str.contains(term, na=False) |
        df['category'].str.lower().str.contains(term, na=False) |
        df['tags'].str.lower().str.contains(term, na=False)
    )
    return df[mask]


# ============================================
# DISPLAY COMPONENTS
# ============================================
def show_metric(value, label, icon="📊"):
    """Show metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem;">{icon}</div>
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def show_notebook_card(nb):
    """Display single notebook"""
    # Parse tags
    tags = []
    if nb.get('tags'):
        try:
            tags = json.loads(nb['tags'])
        except:
            tags = [nb['tags']]
    
    tags_html = ''.join([f'<span class="tag">{t}</span>' for t in tags[:8]])
    
    name = nb.get('name', 'Unnamed Notebook')
    category = nb.get('category', 'Other')
    summary = nb.get('summary', nb.get('main_goal', 'No summary available'))
    goal = nb.get('main_goal', 'Not specified')
    lines = nb.get('total_code_lines', 0) or 0
    modified = nb.get('modified_time', 'Unknown')
    if modified and len(str(modified)) > 10:
        modified = str(modified)[:10]
    colab_link = nb.get('colab_link', '#')
    analyzed = nb.get('analyzed', 0)
    account = nb.get('account', 'Unknown')
    
    status = "✅ Analyzed" if analyzed else "⏳ Pending Analysis"
    status_color = "#238636" if analyzed else "#f0883e"
    
    st.markdown(f"""
    <div class="notebook-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div>
                <h3 class="notebook-title">📓 {name}</h3>
                <div style="margin-top: 8px;">
                    <span class="tag tag-category">{category}</span>
                    <span class="tag">{account}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background-color: {status_color}; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; color: white;">
                    {status}
                </span>
            </div>
        </div>
        
        <p class="notebook-info">{summary}</p>
        
        <p class="notebook-info" style="margin-top: 10px;">
            <strong style="color: white;">🎯 Goal:</strong> {goal}
        </p>
        
        <div style="margin: 12px 0;">
            <strong class="notebook-info">🏷️ Technologies:</strong><br>
            {tags_html if tags_html else '<span class="notebook-info">No tags</span>'}
        </div>
        
        <div style="display: flex; gap: 20px; margin: 12px 0; color: #8b949e; font-size: 0.85rem;">
            <span>📝 {lines:,} lines</span>
            <span>🕒 {modified}</span>
        </div>
        
        <div style="margin-top: 15px;">
            <a href="{colab_link}" target="_blank" style="
                display: inline-block;
                background-color: #238636;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                text-align: center;
            ">🚀 Open in Colab</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# MAIN APP
# ============================================
def main():
    """Main application"""
    
    # Initialize
    db_path = init_db()
    
    # Header
    st.markdown("<h1 class='main-title'>🤖 AI Colab Notebook Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Manage and analyze your Google Colab projects</p>", unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Get data
    df, stats = get_db_data(db_path)
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <img src="https://www.gstatic.com/colaboratory/assets/colab-logo.svg" width="60">
            <h3 style="color: #58a6ff; margin-top: 10px;">Colab Manager</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        st.markdown(f"""
        <div class="info-box">
            <p style="margin: 5px 0;">📓 Total: <strong>{stats['total']}</strong></p>
            <p style="margin: 5px 0;">✅ Analyzed: <strong>{stats['analyzed']}</strong></p>
            <p style="margin: 5px 0;">⏳ Pending: <strong>{stats['pending']}</strong></p>
            <p style="margin: 5px 0;">📝 Lines: <strong>{stats['lines']:,}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📂 Navigation")
        page = st.radio("", [
            "🏠 Dashboard",
            "📚 All Notebooks",
            "🔍 Search",
            "📊 Analytics",
            "❓ Help"
        ])
        
        st.markdown("---")
        
        # Database info
        if os.path.exists(db_path):
            size_kb = os.path.getsize(db_path) / 1024
            st.markdown(f"<p class='help-text'>Database: {size_kb:.1f} KB</p>", unsafe_allow_html=True)
    
    # ============================================
    # PAGES
    # ============================================
    
    if page == "🏠 Dashboard":
        show_dashboard(df, stats)
    elif page == "📚 All Notebooks":
        show_notebooks(df)
    elif page == "🔍 Search":
        show_search(df)
    elif page == "📊 Analytics":
        show_analytics(stats, df)
    elif page == "❓ Help":
        show_help()


def show_dashboard(df, stats):
    """Dashboard page"""
    st.header("📊 Dashboard Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_metric(stats['total'], "Total Notebooks", "📓")
    with col2:
        show_metric(stats['analyzed'], "AI Analyzed", "🧠")
    with col3:
        show_metric(stats['pending'], "Pending", "⏳")
    with col4:
        show_metric(stats['lines'], "Code Lines", "📝")
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Recent notebooks
    st.header("🕒 Recent Notebooks")
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="padding: 40px; text-align: center;">
            <h3 style="color: #58a6ff;">👋 Welcome!</h3>
            <p class="help-text" style="margin-top: 15px;">
                No notebooks found in the database.
            </p>
            <p class="help-text" style="margin-top: 15px;">
                To get started:
            </p>
            <ol style="text-align: left; display: inline-block; margin-top: 15px;" class="help-text">
                <li>Run <code>scanner.py</code> locally to scan your Google Drive</li>
                <li>Run <code>agent.py</code> locally to analyze with AI</li>
                <li>Upload the updated <code>database.db</code> file here</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show first 5 recent
        for _, nb in df.head(5).iterrows():
            show_notebook_card(nb)
    
    # Categories overview
    if stats['categories']:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.header("📂 Categories")
        
        cols = st.columns(min(4, len(stats['categories'])))
        
        for i, (cat, count) in enumerate(list(stats['categories'].items())[:4]):
            with cols[i]:
                show_metric(count, cat, "📁")


def show_notebooks(df):
    """All notebooks page"""
    st.header("📚 All Notebooks")
    
    if df.empty:
        st.warning("No notebooks found. Upload a database file or run scanner locally.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted([c for c in df['category'].dropna().unique() if c])
        selected_cat = st.selectbox("Category", categories)
    
    with col2:
        accounts = ['All'] + sorted([a for a in df['account'].dropna().unique() if a])
        selected_acc = st.selectbox("Account", accounts)
    
    with col3:
        status = st.selectbox("Status", ["All", "Analyzed", "Pending"])
    
    # Apply filters
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_acc != 'All':
        filtered = filtered[filtered['account'] == selected_acc]
    
    if status == "Analyzed":
        filtered = filtered[filtered['analyzed'] == 1]
    elif status == "Pending":
        filtered = filtered[filtered['analyzed'] == 0]
    
    st.markdown(f"<p class='help-text'>Showing {len(filtered)} of {len(df)} notebooks</p>", unsafe_allow_html=True)
    
    # Display
    for _, nb in filtered.iterrows():
        show_notebook_card(nb)


def show_search(df):
    """Search page"""
    st.header("🔍 Search Notebooks")
    
    search_term = st.text_input(
        "Search by name, category, or tags",
        placeholder="e.g., machine learning, tensorflow, nlp...",
        label_visibility="collapsed"
    )
    
    if search_term:
        results = search_df(df, search_term)
        
        if results.empty:
            st.markdown(f"""
            <div class="info-box" style="text-align: center;">
                <p style="color: #8b949e;">No results found for "{search_term}"</p>
                <p class="help-text">Try different keywords</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"Found {len(results)} results for '{search_term}'")
            
            for _, nb in results.iterrows():
                show_notebook_card(nb)
    else:
        st.markdown("""
        <div class="info-box">
            <h4>💡 Quick Search Suggestions</h4>
            <p class="help-text">Click a button to search for common topics</p>
        </div>
        """, unsafe_allow_html=True)
        
        quick = [
            ("Machine Learning", "machine learning"),
            ("Deep Learning", "deep learning"),
            ("NLP", "nlp"),
            ("TensorFlow", "tensorflow"),
            ("PyTorch", "pytorch"),
            ("Data Analysis", "data analysis"),
        ]
        
        cols = st.columns(3)
        for i, (label, term) in enumerate(quick):
            with cols[i % 3]:
                if st.button(f"🔍 {label}"):
                    results = search_df(df, term)
                    st.success(f"Found {len(results)} results for '{label}'")
                    for _, nb in results.iterrows():
                        show_notebook_card(nb)


def show_analytics(stats, df):
    """Analytics page"""
    st.header("📊 Analytics & Insights")
    
    if df.empty:
        st.warning("No data available. Run scanner locally first.")
        return
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_metric(stats['total'], "Total Notebooks", "📓")
    with col2:
        show_metric(stats['lines'], "Lines of Code", "📝")
    with col3:
        show_metric(len(stats['categories']), "Categories", "📁")
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Category chart
    st.header("📂 Notebooks by Category")
    
    if stats['categories']:
        import plotly.express as px
        
        cats = list(stats['categories'].keys())
        counts = list(stats['categories'].values())
        
        fig = px.pie(
            names=cats,
            values=counts,
            title="Distribution by Category",
            hole=0.4
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(font_color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Top technologies
    st.header("🏷️ Top Technologies Used")
    
    all_tags = []
    for tags_str in df['tags'].dropna():
        try:
            tags = json.loads(tags_str)
            all_tags.extend(tags)
        except:
            pass
    
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags).most_common(15)
        
        tags_df = pd.DataFrame(tag_counts, columns=['Technology', 'Count'])
        
        fig = px.bar(
            tags_df,
            x='Count',
            y='Technology',
            orientation='h',
            title="Most Used Technologies"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_help():
    """Help page"""
    st.header("❓ Help & Setup Guide")
    
    with st.expander("🚀 Quick Start Guide", expanded=True):
        st.markdown("""
        **To use this dashboard, you need to process your notebooks locally first:**
        
        **Step 1: Install dependencies**
        ```
        pip install -r requirements.txt
        ```
        
        **Step 2: Run Scanner**
        ```
        python scanner.py
        ```
        This scans your Google Drive for Colab notebooks.
        
        **Step 3: Run AI Analyzer**
        ```
        python agent.py
        ```
        This analyzes notebooks using Google Gemini AI.
        
        **Step 4: Upload Database**
        - The `database.db` file will be created
        - Upload it using the file uploader in this app
        - Or upload to GitHub for Streamlit Cloud deployment
        """)
    
    with st.expander("📁 File Structure"):
        st.markdown("""
        ```
        colab-analyzer/
        ├── app.py              ← This dashboard
        ├── scanner.py         ← Scans Google Drive
        ├── agent.py           ← AI analysis
        ├── requirements.txt   ← Dependencies
        ├── database.db        ← Created by scanner (upload here)
        └── .env               ← Your API keys
        ```
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Dashboard is empty:**
        - Run `scanner.py` locally
        - Run `agent.py` locally  
        - Upload the `database.db` file
        
        **Scanner errors:**
        - Set up Google Cloud service account
        - Share your Drive folders with service account
        
        **Agent errors:**
        - Get Gemini API key from https://aistudio.google.com/app/apikey
        - Add to `.env` file: `GEMINI_API_KEY=your_key`
        """)
    
    with st.expander("📤 How to Upload Database"):
        st.markdown("""
        **For Local Development:**
        1. Run scanner.py and agent.py locally
        2. The database.db file will be created
        3. Dashboard will automatically read it
        
        **For Streamlit Cloud:**
        1. Commit database.db to GitHub
        2. App will read from GitHub
        3. Or add database as a secret in Streamlit Cloud settings
        """)


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()
