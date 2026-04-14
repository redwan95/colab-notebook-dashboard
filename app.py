"""
Streamlit Cloud-Ready Colab Notebook Manager
Works without local scanner - reads pre-uploaded database
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# MUST BE FIRST
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with dark mode support and readable text
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content area - WHITE background with BLACK text */
    .block-container {
        background: #ffffff !important;
        border-radius: 20px;
        padding: 2rem !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        max-width: 1200px;
        margin: 2rem auto;
    }
    
    /* All text should be dark */
    .block-container p,
    .block-container h1,
    .block-container h2,
    .block-container h3,
    .block-container h4,
    .block-container div,
    .block-container span,
    .block-container label {
        color: #1a1a1a !important;
    }
    
    /* Header */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Metric boxes */
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 15px 0;
        cursor: pointer;
    }
    
    .metric-box:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    .metric-box h2 {
        font-size: 3.5rem !important;
        margin: 0 !important;
        font-weight: 800 !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-box p {
        font-size: 1.3rem !important;
        margin: 10px 0 0 0 !important;
        opacity: 0.95;
        color: white !important;
        font-weight: 600;
    }
    
    /* Notebook cards */
    .notebook-card {
        border: 3px solid #e8e8e8;
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
    }
    
    .notebook-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .notebook-card:hover {
        transform: translateX(10px) translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .notebook-card h3 {
        color: #2d3748 !important;
        margin-top: 0 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 15px !important;
    }
    
    .notebook-card p {
        color: #4a5568 !important;
        line-height: 1.8;
        margin: 10px 0 !important;
        font-size: 1.05rem !important;
    }
    
    .notebook-card strong {
        color: #1a202c !important;
        font-weight: 700;
    }
    
    /* Tags */
    .tag {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 10px 18px;
        border-radius: 25px;
        margin: 5px;
        display: inline-block;
        font-size: 0.95rem !important;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .tag:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.6);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 15px 35px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Info/Warning/Success boxes */
    .element-container div[data-testid="stMarkdownContainer"] div {
        color: #1a1a1a !important;
    }
    
    .info-box {
        background: #e3f2fd !important;
        border-left: 6px solid #2196F3 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin: 20px 0 !important;
        color: #0d47a1 !important;
    }
    
    .info-box * {
        color: #0d47a1 !important;
    }
    
    .success-box {
        background: #e8f5e9 !important;
        border-left: 6px solid #4CAF50 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin: 20px 0 !important;
        color: #1b5e20 !important;
    }
    
    .success-box * {
        color: #1b5e20 !important;
    }
    
    .warning-box {
        background: #fff3e0 !important;
        border-left: 6px solid #ff9800 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        margin: 20px 0 !important;
        color: #e65100 !important;
    }
    
    .warning-box * {
        color: #e65100 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* File uploader */
    .uploadedFile {
        background: white !important;
        color: black !important;
    }
    
    /* Selectbox and input */
    .stSelectbox label,
    .stTextInput label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* Tables */
    .dataframe {
        color: #1a1a1a !important;
    }
    
    /* Make sure all Streamlit components have dark text */
    .stMarkdown,
    .stText {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Database class
class NotebookDatabase:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.ensure_database_exists()
        
    def ensure_database_exists(self):
        """Create database if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notebooks (
                    id TEXT PRIMARY KEY,
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
                    analyzed BOOLEAN DEFAULT 0,
                    summary TEXT,
                    tags TEXT,
                    category TEXT,
                    main_goal TEXT,
                    key_findings TEXT,
                    technologies TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"❌ Database error: {e}")
    
    def get_all_notebooks(self):
        """Get all notebooks"""
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()
            
            conn = sqlite3.connect(self.db_path)
            query = "SELECT * FROM notebooks ORDER BY modified_time DESC"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"❌ Error loading notebooks: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get statistics"""
        try:
            if not os.path.exists(self.db_path):
                return {'total': 0, 'analyzed': 0, 'by_category': {}, 'total_lines': 0}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute("SELECT COUNT(*) FROM notebooks")
            stats['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notebooks WHERE analyzed = 1")
            stats['analyzed'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM notebooks 
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
            """)
            stats['by_category'] = dict(cursor.fetchall())
            
            cursor.execute("SELECT COALESCE(SUM(total_code_lines), 0) FROM notebooks")
            stats['total_lines'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
        except Exception as e:
            return {'total': 0, 'analyzed': 0, 'by_category': {}, 'total_lines': 0}
    
    def search_notebooks(self, search_term):
        """Search notebooks"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f"""
                SELECT * FROM notebooks 
                WHERE name LIKE '%{search_term}%' 
                OR summary LIKE '%{search_term}%'
                OR tags LIKE '%{search_term}%'
                OR category LIKE '%{search_term}%'
                ORDER BY modified_time DESC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"❌ Search error: {e}")
            return pd.DataFrame()
    
    def upload_database(self, uploaded_file):
        """Upload database from file"""
        try:
            with open(self.db_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            return True
        except Exception as e:
            st.error(f"❌ Upload error: {e}")
            return False

def display_notebook_card(notebook):
    """Display notebook card"""
    try:
        tags = json.loads(notebook['tags']) if notebook['tags'] and notebook['tags'] != 'null' else []
    except:
        tags = []
    
    tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in tags[:8]])
    
    # Safely get values
    name = str(notebook.get('name', 'Unnamed'))[:100]
    account = str(notebook.get('account', 'Unknown'))
    category = str(notebook.get('category', 'Uncategorized'))
    summary = str(notebook.get('summary', 'Not analyzed yet'))[:300]
    main_goal = str(notebook.get('main_goal', 'Not specified'))[:200]
    key_findings = str(notebook.get('key_findings', 'N/A'))[:200]
    total_lines = int(notebook.get('total_code_lines', 0))
    modified_time = str(notebook.get('modified_time', 'Unknown'))[:10]
    
    st.markdown(f"""
    <div class='notebook-card'>
        <h3>📓 {name}</h3>
        <p><strong>👤 Account:</strong> {account}</p>
        <p><strong>📁 Category:</strong> {category}</p>
        <p><strong>📝 Summary:</strong> {summary}</p>
        <p><strong>🎯 Main Goal:</strong> {main_goal}</p>
        <p><strong>💡 Key Findings:</strong> {key_findings}</p>
        <p><strong>📊 Lines of Code:</strong> {total_lines:,}</p>
        <p><strong>🏷️ Tags:</strong><br>{tags_html if tags_html else '<em>No tags</em>'}</p>
        <p><small>🕒 Last Modified: {modified_time}</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Buttons
    col1, col2 = st.columns(2)
    
    colab_link = notebook.get('colab_link', '')
    web_link = notebook.get('web_link', '')
    
    with col1:
        if colab_link:
            st.link_button("🚀 Open in Colab", colab_link, use_container_width=True)
    
    with col2:
        if web_link:
            st.link_button("📂 Open in Drive", web_link, use_container_width=True)

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI-Powered Colab Manager</h1>", unsafe_allow_html=True)
    
    # Initialize database
    db = NotebookDatabase()
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.gstatic.com/colaboratory/assets/colab-logo.svg", width=150)
        st.markdown("<h2 style='color: white !important;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Upload database
        st.markdown("<h3 style='color: white !important;'>📤 Upload Database</h3>", unsafe_allow_html=True)
        uploaded_db = st.file_uploader(
            "Upload database.db file",
            type=['db'],
            help="Upload your database.db file from local machine",
            key="db_upload"
        )
        
        if uploaded_db:
            if db.upload_database(uploaded_db):
                st.success("✅ Database uploaded!")
                st.rerun()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("<h3 style='color: white !important;'>📍 Navigation</h3>", unsafe_allow_html=True)
        page = st.radio(
            "Choose page:",
            ["🏠 Dashboard", "📚 All Notebooks", "🔍 Search", "📊 Analytics", "ℹ️ Help"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Stats
        st.markdown("<h3 style='color: white !important;'>📊 Quick Stats</h3>", unsafe_allow_html=True)
        stats = db.get_statistics()
        
        st.metric("Total Notebooks", stats['total'])
        st.metric("AI Analyzed", stats['analyzed'])
        st.metric("Code Lines", f"{stats['total_lines']:,}")
        
        if stats['total'] > 0:
            progress = stats['analyzed'] / stats['total'] if stats['total'] > 0 else 0
            st.progress(progress)
            st.caption(f"{int(progress*100)}% analyzed")
    
    # Main content
    if stats['total'] == 0:
        show_welcome_screen()
    elif page == "🏠 Dashboard":
        show_dashboard(db, stats)
    elif page == "📚 All Notebooks":
        show_all_notebooks(db)
    elif page == "🔍 Search":
        show_search(db)
    elif page == "📊 Analytics":
        show_analytics(db)
    elif page == "ℹ️ Help":
        show_help()

def show_welcome_screen():
    """Welcome screen"""
    st.markdown("""
    <div class='info-box'>
        <h2>👋 Welcome to AI Colab Manager!</h2>
        <p style='font-size: 1.2rem;'>Upload your database.db file to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Quick Start
        
        **On Streamlit Cloud:**
        1. Run scanner locally on your computer
        2. Upload the `database.db` file using sidebar
        3. Explore your notebooks!
        
        **Locally (Full Features):**
        1. Run: `python scanner.py Account1`
        2. Run: `python agent.py`
        3. Run: `streamlit run app.py`
        
        ### ✨ Features
        
        - 📊 AI-powered analysis
        - 🔍 Smart search
        - 📈 Beautiful analytics
        - 🏷️ Automatic tagging
        """)
    
    with col2:
        st.markdown("""
        ### 📋 How to Get database.db
        
        **On your local computer:**
        
        ```bash
        # 1. Scan your notebooks
        python scanner.py Account1
        
        # 2. Analyze with AI
        python agent.py
        
        # 3. Find database.db in folder
        # 4. Upload it here!
        ```
        
        ### 📍 File Location
        
        The `database.db` file is in your:
        - Windows: `C:\\ColabAnalyzer\\database.db`
        - Mac/Linux: `~/ColabAnalyzer/database.db`
        """)
    
    # Download section
    st.markdown("---")
    st.subheader("💾 Need the Scanner?")
    
    st.info("⬇️ Download the scanner script to run on your computer")
    
    # Provide download for scanner
    st.markdown("""
    **Instructions:**
    1. Download `scanner.py` and `agent.py` from the GitHub repo
    2. Run them locally to generate `database.db`
    3. Upload `database.db` here
    """)

def show_dashboard(db, stats):
    """Dashboard"""
    st.markdown("<h2 style='color: #1a1a1a !important;'>📊 Dashboard Overview</h2>", unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <h2>{stats['total']}</h2>
            <p>Total Notebooks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-box'>
            <h2>{stats['analyzed']}</h2>
            <p>AI Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending = stats['total'] - stats['analyzed']
        st.markdown(f"""
        <div class='metric-box'>
            <h2>{pending}</h2>
            <p>Pending</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-box'>
            <h2>{stats['total_lines']:,}</h2>
            <p>Lines of Code</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h3 style='color: #1a1a1a !important;'>🕒 Recently Modified</h3>", unsafe_allow_html=True)
        df = db.get_all_notebooks()
        
        if not df.empty:
            recent = df.head(5)
            for _, nb in recent.iterrows():
                display_notebook_card(nb)
        else:
            st.info("No notebooks yet")
    
    with col2:
        st.markdown("<h3 style='color: #1a1a1a !important;'>📁 Categories</h3>", unsafe_allow_html=True)
        
        if stats['by_category']:
            fig = px.pie(
                values=list(stats['by_category'].values()),
                names=list(stats['by_category'].keys()),
                color_discrete_sequence=px.colors.sequential.Purples,
                hole=0.4
            )
            fig.update_layout(
                showlegend=True,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Run AI analysis to see categories")

def show_all_notebooks(db):
    """All notebooks page"""
    st.markdown("<h2 style='color: #1a1a1a !important;'>📚 All Notebooks</h2>", unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.warning("⚠️ No notebooks found. Upload database.db file.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted([str(c) for c in df['category'].dropna().unique() if c])
        selected_cat = st.selectbox("📁 Category", categories, key="cat_filter")
    
    with col2:
        accounts = ['All'] + sorted([str(a) for a in df['account'].unique()])
        selected_account = st.selectbox("👤 Account", accounts, key="acc_filter")
    
    with col3:
        sort_by = st.selectbox("🔀 Sort by", ["Recent", "Name", "Size"], key="sort_filter")
    
    # Apply filters
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_account != 'All':
        filtered = filtered[filtered['account'] == selected_account]
    
    # Sort
    if sort_by == "Recent":
        filtered = filtered.sort_values('modified_time', ascending=False, na_position='last')
    elif sort_by == "Name":
        filtered = filtered.sort_values('name')
    elif sort_by == "Size":
        filtered = filtered.sort_values('total_code_lines', ascending=False, na_position='last')
    
    st.markdown(f"<p style='color: #1a1a1a !important; font-size: 1.1rem;'>📊 Showing <strong>{len(filtered)}</strong> of <strong>{len(df)}</strong> notebooks</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display
    for _, nb in filtered.iterrows():
        display_notebook_card(nb)

def show_search(db):
    """Search page"""
    st.markdown("<h2 style='color: #1a1a1a !important;'>🔍 Search Notebooks</h2>", unsafe_allow_html=True)
    
    search_term = st.text_input(
        "🔎 Enter search term",
        placeholder="Search by name, summary, tags, or category...",
        key="search_input"
    )
    
    if search_term:
        results = db.search_notebooks(search_term)
        
        if not results.empty:
            st.markdown(f"<div class='success-box'><p>✅ Found <strong>{len(results)}</strong> results for '<strong>{search_term}</strong>'</p></div>", unsafe_allow_html=True)
            
            for _, nb in results.iterrows():
                display_notebook_card(nb)
        else:
            st.markdown(f"<div class='warning-box'><p>⚠️ No results found for '<strong>{search_term}</strong>'</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-box'><p>👆 Enter a search term above to find notebooks</p></div>", unsafe_allow_html=True)

def show_analytics(db):
    """Analytics page"""
    st.markdown("<h2 style='color: #1a1a1a !important;'>📊 Analytics & Insights</h2>", unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.warning("⚠️ No data available")
        return
    
    # Category pie chart
    st.markdown("<h3 style='color: #1a1a1a !important;'>📂 Distribution by Category</h3>", unsafe_allow_html=True)
    
    if 'category' in df.columns:
        category_counts = df['category'].value_counts()
        
        if not category_counts.empty:
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                color_discrete_sequence=px.colors.sequential.Purples
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.markdown("<h3 style='color: #1a1a1a !important;'>📈 Creation Timeline</h3>", unsafe_allow_html=True)
    
    if 'created_time' in df.columns:
        df['created_date'] = pd.to_datetime(df['created_time'], errors='coerce').dt.date
        timeline = df.groupby('created_date').size().reset_index(name='count')
        timeline = timeline.dropna()
        
        if not timeline.empty:
            fig = px.area(
                timeline,
                x='created_date',
                y='count',
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #1a1a1a !important;'>👤 By Account</h3>", unsafe_allow_html=True)
        account_counts = df['account'].value_counts()
        
        fig = px.bar(
            x=account_counts.index,
            y=account_counts.values,
            labels={'x': 'Account', 'y': 'Count'},
            color=account_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='color: #1a1a1a !important;'>📊 Code Distribution</h3>", unsafe_allow_html=True)
        
        fig = px.histogram(
            df,
            x='total_code_lines',
            nbins=20,
            color_discrete_sequence=['#764ba2']
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tags
    st.markdown("<h3 style='color: #1a1a1a !important;'>🏷️ Most Popular Tags</h3>", unsafe_allow_html=True)
    
    all_tags = []
    for tags_str in df['tags'].dropna():
        try:
            tags = json.loads(tags_str)
            if isinstance(tags, list):
                all_tags.extend(tags)
        except:
            pass
    
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts().head(20)
        
        fig = px.bar(
            x=tag_counts.values,
            y=tag_counts.index,
            orientation='h',
            labels={'x': 'Count', 'y': 'Tag'},
            color=tag_counts.values,
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def show_help():
    """Help page"""
    st.markdown("<h2 style='color: #1a1a1a !important;'>ℹ️ Help & Documentation</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 Getting Started", "💻 Local Setup", "🐛 Troubleshooting"])
    
    with tab1:
        st.markdown("""
        ## 🚀 Getting Started
        
        ### On Streamlit Cloud (Current)
        
        1. **Generate database locally:**
           ```bash
           python scanner.py Account1
           python agent.py
           ```
        
        2. **Upload database:**
           - Find `database.db` in your folder
           - Upload using sidebar uploader
        
        3. **Explore:**
           - View dashboard
           - Search notebooks
           - See analytics
        
        ### Features Available
        
        - ✅ View all notebooks
        - ✅ Search and filter
        - ✅ Analytics charts
        - ✅ Category breakdown
        - ❌ Scanning (local only)
        - ❌ AI analysis (local only)
        """)
    
    with tab2:
        st.markdown("""
        ## 💻 Local Installation
        
        ### Requirements
        
        - Python 3.8+
        - Google account
        - Gemini API key
        
        ### Setup Steps
        
        1. **Clone repository:**
           ```bash
           git clone https://github.com/your-repo/colab-analyzer
           cd colab-analyzer
           ```
        
        2. **Install dependencies:**
           ```bash
           pip install -r requirements.txt
           ```
        
        3. **Configure:**
           - Add `credentials.json`
           - Create `.env` with `GEMINI_API_KEY`
        
        4. **Run:**
           ```bash
           python scanner.py Account1
           python agent.py
           streamlit run app.py
           ```
        """)
    
    with tab3:
        st.markdown("""
        ## 🐛 Troubleshooting
        
        ### Common Issues
        
        **Q: Database not loading?**
        - Make sure you uploaded `database.db` not `database.sqlite`
        - File must be exactly named `database.db`
        
        **Q: No notebooks showing?**
        - Ensure database was generated with scanner
        - Check database has data: should be > 1KB
        
        **Q: Buttons not working?**
        - Refresh the page
        - Clear browser cache
        - Try different browser
        
        **Q: Charts not displaying?**
        - Make sure notebooks are analyzed
        - Run `python agent.py` locally
        
        ### Need More Help?
        
        - 📧 Email: support@example.com
        - 💬 GitHub Issues: [Create Issue](https://github.com)
        - 📚 Documentation: [Read Docs](https://docs.example.com)
        """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error")
        st.code(f"{type(e).__name__}: {str(e)}")
        
        with st.expander("🔍 Full Error Details"):
            import traceback
            st.code(traceback.format_exc())
