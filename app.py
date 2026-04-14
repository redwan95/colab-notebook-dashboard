"""
AI-Powered Colab Notebook Manager - Enhanced Dashboard
Beautiful, user-friendly interface with dark mode support
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import os
from dotenv import load_dotenv
import streamlit as st
import os
from dotenv import load_dotenv

# Load local .env if it exists (for local testing)
load_dotenv()

# Get the key from Streamlit Secrets (Cloud) or Environment (Local)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API Key is missing. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()


load_dotenv()
"""
AI-Powered Colab Notebook Manager - Stable Version
Robust, error-free, works on Streamlit Cloud
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS STYLING - Dark Beautiful Theme
# ==========================================
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }
    
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    /* Metric boxes */
    .metric-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid #475569;
        text-align: center;
        transition: all 0.3s;
    }
    
    .metric-box:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6366f1;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Notebook cards */
    .notebook-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #334155;
        transition: all 0.3s;
        position: relative;
    }
    
    .notebook-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1, #ec4899);
        border-radius: 4px 0 0 4px;
    }
    
    .notebook-card:hover {
        transform: translateX(5px);
        border-color: #6366f1;
    }
    
    /* Tags */
    .tag {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        display: inline-block;
        font-size: 0.85rem;
    }
    
    .tag-category {
        background: linear-gradient(135deg, #ec4899, #f43f5e);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-left: 4px solid #6366f1;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }
    
    /* Text colors */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #475569 !important;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-green { background: #10b981; }
    .status-yellow { background: #f59e0b; }
    .status-blue { background: #6366f1; }
    
    /* Stats in sidebar */
    .sidebar-stats {
        background: #1e293b;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    /* Section header */
    .section-header {
        color: #f1f5f9;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #334155;
    }
    
    /* Links */
    a {
        color: #6366f1 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #f1f5f9;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
    }
    
    /* Success/Error messages */
    .success-box {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #991b1b 0%, #b91c1c 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE CLASS
# ==========================================
class NotebookDatabase:
    """Handle all database operations"""
    
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.close()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
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
    
    def get_all_notebooks(self):
        """Get all notebooks"""
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()
            
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM notebooks ORDER BY modified_time DESC", conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading notebooks: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get summary statistics"""
        stats = {
            'total': 0,
            'analyzed': 0,
            'pending': 0,
            'by_category': {},
            'by_account': {},
            'total_lines': 0
        }
        
        try:
            if not os.path.exists(self.db_path):
                return stats
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM notebooks")
            stats['total'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM notebooks WHERE analyzed = 1")
            stats['analyzed'] = cursor.fetchone()[0] or 0
            
            stats['pending'] = stats['total'] - stats['analyzed']
            
            cursor.execute("SELECT category, COUNT(*) FROM notebooks WHERE category IS NOT NULL GROUP BY category")
            stats['by_category'] = dict(cursor.fetchall())
            
            cursor.execute("SELECT account, COUNT(*) FROM notebooks GROUP BY account")
            stats['by_account'] = dict(cursor.fetchall())
            
            cursor.execute("SELECT SUM(total_code_lines) FROM notebooks WHERE total_code_lines IS NOT NULL")
            stats['total_lines'] = cursor.fetchone()[0] or 0
            
            conn.close()
        except Exception as e:
            print(f"Error getting stats: {e}")
        
        return stats
    
    def search_notebooks(self, search_term):
        """Search notebooks"""
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()
            
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT * FROM notebooks 
                WHERE name LIKE ? OR summary LIKE ? OR tags LIKE ? OR category LIKE ?
                ORDER BY modified_time DESC
            """
            search = f"%{search_term}%"
            df = pd.read_sql_query(query, conn, params=(search, search, search, search))
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error searching: {e}")
            return pd.DataFrame()
    
    def get_recent_notebooks(self, limit=5):
        """Get recent notebooks"""
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()
            
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                f"SELECT * FROM notebooks ORDER BY modified_time DESC LIMIT {limit}", 
                conn
            )
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def display_metric_card(value, label, icon="📊"):
    """Display a metric card"""
    st.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <p class="metric-value">{value:,}</p>
        <p class="metric-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def display_notebook_card(notebook):
    """Display a notebook as a card"""
    try:
        # Parse tags
        tags_str = notebook.get('tags', '')
        if tags_str:
            try:
                tags = json.loads(tags_str)
            except:
                tags = [tags_str]
        else:
            tags = []
        
        tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in tags[:8]])
        
        # Get values with defaults
        name = notebook.get('name', 'Unnamed Notebook')
        category = notebook.get('category', 'Uncategorized')
        summary = notebook.get('summary', notebook.get('main_goal', 'No summary available'))
        main_goal = notebook.get('main_goal', 'Not specified')
        code_lines = notebook.get('total_code_lines', 0) or 0
        modified = notebook.get('modified_time', 'Unknown')
        analyzed = notebook.get('analyzed', 0)
        account = notebook.get('account', 'Unknown')
        colab_link = notebook.get('colab_link', '#')
        web_link = notebook.get('web_link', '#')
        
        # Status indicator
        if analyzed:
            status_html = "<span class='status-indicator status-green'></span>✅ Analyzed"
        else:
            status_html = "<span class='status-indicator status-yellow'></span>⏳ Pending"
        
        st.markdown(f"""
        <div class="notebook-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: #f1f5f9; margin: 0;">📓 {name}</h3>
                    <div style="margin-top: 10px;">
                        <span class="tag tag-category">{category}</span>
                        <span class="tag">{account}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    {status_html}
                </div>
            </div>
            
            <p style="color: #cbd5e1; margin: 15px 0; line-height: 1.6;">
                {summary}
            </p>
            
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 10px 0;">
                <strong style="color: #f1f5f9;">🎯 Goal:</strong> {main_goal}
            </p>
            
            <div style="margin: 15px 0;">
                <strong style="color: #94a3b8;">🏷️ Technologies:</strong><br>
                {tags_html}
            </div>
            
            <div style="display: flex; gap: 20px; margin: 15px 0; color: #94a3b8; font-size: 0.85rem;">
                <span>📝 {code_lines:,} lines</span>
                <span>🕒 {modified[:10] if modified else 'Unknown'}</span>
            </div>
            
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <a href="{colab_link}" target="_blank" style="
                    background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 10px;
                    text-decoration: none;
                    font-weight: 600;
                    flex: 1;
                    text-align: center;
                ">🚀 Open in Colab</a>
                
                <a href="{web_link}" target="_blank" style="
                    background: #1e293b;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 10px;
                    text-decoration: none;
                    font-weight: 600;
                    flex: 1;
                    text-align: center;
                    border: 1px solid #475569;
                ">📂 Drive Link</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying notebook: {e}")


# ==========================================
# MAIN APP
# ==========================================
def main():
    """Main app function"""
    
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI Colab Manager</h1>", unsafe_allow_html=True)
    
    # Initialize database
    db = NotebookDatabase()
    stats = db.get_statistics()
    
    # ==========================================
    # SIDEBAR
    # ==========================================
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 15px 0;">
            <img src="https://www.gstatic.com/colaboratory/assets/colab-logo.svg" width="60">
            <h2 style="color: #f1f5f9; margin-top: 10px; font-size: 1.2rem;">Colab Manager</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        st.markdown(f"""
        <div class="sidebar-stats">
            <p style="color: #f1f5f9; margin: 8px 0;">
                <span class='status-indicator status-blue'></span>
                Total: <strong>{stats['total']}</strong>
            </p>
            <p style="color: #f1f5f9; margin: 8px 0;">
                <span class='status-indicator status-green'></span>
                Analyzed: <strong>{stats['analyzed']}</strong>
            </p>
            <p style="color: #f1f5f9; margin: 8px 0;">
                <span class='status-indicator status-yellow'></span>
                Pending: <strong>{stats['pending']}</strong>
            </p>
            <p style="color: #f1f5f9; margin: 8px 0;">
                📝 Lines: <strong>{stats['total_lines']:,}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Instructions
        with st.expander("📖 How to Use"):
            st.markdown("""
            **First Time Setup:**
            1. Run `scanner.py` to scan Drive
            2. Run `agent.py` to analyze with AI
            3. Refresh this page
            
            **Navigation:**
            - Use the tabs below to browse
            - Use search to find notebooks
            
            **Tips:**
            - Click "Open in Colab" to jump directly to a notebook
            """)
        
        st.markdown("---")
        
        # Navigation radio
        selected = st.radio(
            "Navigation",
            ["🏠 Dashboard", "📚 All Notebooks", "🔍 Search", "📊 Analytics", "⚙️ Help"],
            label_visibility="collapsed"
        )
    
    # ==========================================
    # PAGE CONTENT
    # ==========================================
    
    if selected == "🏠 Dashboard":
        show_dashboard(db, stats)
    
    elif selected == "📚 All Notebooks":
        show_all_notebooks(db)
    
    elif selected == "🔍 Search":
        show_search(db)
    
    elif selected == "📊 Analytics":
        show_analytics(db, stats)
    
    elif selected == "⚙️ Help":
        show_help()


# ==========================================
# PAGES
# ==========================================
def show_dashboard(db, stats):
    """Dashboard page"""
    st.markdown('<p class="section-header">📊 Overview</p>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric_card(stats['total'], "Total", "📓")
    with col2:
        display_metric_card(stats['analyzed'], "Analyzed", "🧠")
    with col3:
        display_metric_card(stats['pending'], "Pending", "⏳")
    with col4:
        display_metric_card(stats['total_lines'], "Lines", "📝")
    
    st.markdown("---")
    
    # Recent notebooks
    st.markdown('<p class="section-header">🕒 Recent Notebooks</p>', unsafe_allow_html=True)
    
    df = db.get_recent_notebooks(5)
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 40px;">
            <h3 style="color: #f1f5f9;">👋 Welcome!</h3>
            <p style="color: #94a3b8; margin-top: 10px;">
                No notebooks found. Run the scanner first!
            </p>
            <p style="color: #94a3b8; margin-top: 10px;">
                1. Open terminal in project folder<br>
                2. Run: <code>python scanner.py</code><br>
                3. Run: <code>python agent.py</code><br>
                4. Refresh this page
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for _, nb in df.iterrows():
            display_notebook_card(nb)
    
    # Category overview
    if stats['by_category']:
        st.markdown("---")
        st.markdown('<p class="section-header">📂 Categories</p>', unsafe_allow_html=True)
        
        # Create columns for categories
        categories = list(stats['by_category'].keys())
        cols = st.columns(min(4, len(categories)))
        
        for i, cat in enumerate(categories[:4]):
            with cols[i]:
                count = stats['by_category'][cat]
                st.metric(cat, count)


def show_all_notebooks(db):
    """All notebooks page"""
    st.markdown('<p class="section-header">📚 All Notebooks</p>', unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.info("No notebooks found. Run the scanner first!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted([c for c in df['category'].dropna().unique() if c])
        selected_cat = st.selectbox("📁 Category", categories)
    
    with col2:
        accounts = ['All'] + sorted([a for a in df['account'].unique() if a])
        selected_account = st.selectbox("👤 Account", accounts)
    
    with col3:
        status_filter = st.selectbox("📊 Status", ["All", "Analyzed", "Pending"])
    
    # Apply filters
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_account != 'All':
        filtered = filtered[filtered['account'] == selected_account]
    
    if status_filter == "Analyzed":
        filtered = filtered[filtered['analyzed'] == 1]
    elif status_filter == "Pending":
        filtered = filtered[filtered['analyzed'] == 0]
    
    st.info(f"Showing {len(filtered)} of {len(df)} notebooks")
    
    # Display
    for _, nb in filtered.iterrows():
        display_notebook_card(nb)


def show_search(db):
    """Search page"""
    st.markdown('<p class="section-header">🔍 Search Notebooks</p>', unsafe_allow_html=True)
    
    search_term = st.text_input(
        "Search",
        placeholder="Type to search (e.g., machine learning, tensorflow, nlp)...",
        label_visibility="collapsed"
    )
    
    if search_term:
        results = db.search_notebooks(search_term)
        
        if results.empty:
            st.markdown("""
            <div class="info-box" style="text-align: center;">
                <p style="color: #94a3b8;">No results found for your search.</p>
                <p style="color: #94a3b8;">Try different keywords.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success(f"Found {len(results)} results for '{search_term}'")
            
            for _, nb in results.iterrows():
                display_notebook_card(nb)
    else:
        # Quick search suggestions
        st.markdown("### 💡 Quick Search")
        
        suggestions = [
            ("Machine Learning", "machine learning"),
            ("Deep Learning", "deep learning"),
            ("NLP", "nlp"),
            ("TensorFlow", "tensorflow"),
            ("PyTorch", "pytorch"),
            ("Data Analysis", "data analysis"),
        ]
        
        cols = st.columns(3)
        
        for i, (label, term) in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(f"🔍 {label}", key=f"search_{i}"):
                    st.session_state['search_term'] = term
                    results = db.search_notebooks(term)
                    
                    st.success(f"Found {len(results)} results")
                    for _, nb in results.iterrows():
                        display_notebook_card(nb)


def show_analytics(db, stats):
    """Analytics page"""
    st.markdown('<p class="section-header">📊 Analytics</p>', unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.info("No data available. Scan your notebooks first!")
        return
    
    # Top metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_metric_card(stats['total'], "Total Notebooks", "📓")
    with col2:
        display_metric_card(stats['total_lines'], "Total Code Lines", "📝")
    with col3:
        display_metric_card(len(stats['by_category']), "Categories", "📁")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📂 By Category")
        
        if stats['by_category']:
            fig = px.pie(
                values=list(stats['by_category'].values()),
                names=list(stats['by_category'].keys()),
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Purples
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f1f5f9',
                legend=dict(font_color='#f1f5f9')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 👤 By Account")
        
        if stats['by_account']:
            fig = px.bar(
                x=list(stats['by_account'].keys()),
                y=list(stats['by_account'].values()),
                color=list(stats['by_account'].values()),
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#f1f5f9'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Popular tags
    st.markdown("### 🏷️ Top Technologies")
    
    all_tags = []
    for tags_str in df['tags'].dropna():
        try:
            tags = json.loads(tags_str)
            all_tags.extend(tags)
        except:
            pass
    
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts().head(15)
        
        fig = px.bar(
            x=tag_counts.values,
            y=tag_counts.index,
            orientation='h',
            color=tag_counts.values,
            color_continuous_scale='Teal'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#f1f5f9'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_help():
    """Help page"""
    st.markdown('<p class="section-header">⚙️ Help & Information</p>', unsafe_allow_html=True)
    
    with st.expander("🚀 Quick Start Guide", expanded=True):
        st.markdown("""
        **Step 1: Run the Scanner**
        ```
        python scanner.py
        ```
        This scans your Google Drive for Colab notebooks.
        
        **Step 2: Run the AI Analyzer**
        ```
        python agent.py
        ```
        This analyzes your notebooks using Google Gemini AI.
        
        **Step 3: View Dashboard**
        ```
        python -m streamlit run app.py
        ```
        Open http://localhost:8501 in your browser.
        """)
    
