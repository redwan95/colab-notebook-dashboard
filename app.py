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

# Page configuration
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for beautiful UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main theme */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Dark mode body */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 30px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 25px;
        border: 1px solid #475569;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: #6366f1;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: #6366f1;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Notebook cards */
    .notebook-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid #334155;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .notebook-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1, #ec4899);
    }
    
    .notebook-card:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        border-color: #6366f1;
    }
    
    /* Tags */
    .tag {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        margin: 4px;
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .tag-category {
        background: linear-gradient(135deg, #ec4899, #f43f5e);
    }
    
    .tag-status-inprogress {
        background: linear-gradient(135deg, #f59e0b, #eab308);
        color: #000;
    }
    
    .tag-status-completed {
        background: linear-gradient(135deg, #10b981, #059669);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
    }
    
    /* Links */
    a {
        color: #6366f1;
        text-decoration: none;
    }
    
    /* Section headers */
    .section-header {
        color: #f1f5f9;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #334155;
    }
    
    /* Status indicators */
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background: #10b981; }
    .status-pending { background: #f59e0b; }
    .status-analyzed { background: #6366f1; }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #1e293b, #334155);
        border-left: 4px solid #6366f1;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Charts container */
    .chart-container {
        background: #1e293b;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)


# Database helper class
class NotebookDatabase:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        
    def get_all_notebooks(self):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM notebooks ORDER BY modified_time DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM notebooks")
        stats['total'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notebooks WHERE analyzed = 1")
        stats['analyzed'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) as count FROM notebooks WHERE category IS NOT NULL GROUP BY category")
        stats['by_category'] = dict(cursor.fetchall())
        
        cursor.execute("SELECT SUM(total_code_lines) FROM notebooks")
        stats['total_lines'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT account, COUNT(*) as count FROM notebooks GROUP BY account")
        stats['by_account'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def search_notebooks(self, search_term):
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


def display_metric_card(value, label, icon="📊"):
    """Display a beautiful metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2.5rem; margin-bottom: 10px;">{icon}</div>
        <p class="metric-value">{value:,}</p>
        <p class="metric-label">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def display_notebook_card(notebook):
    """Display a beautiful notebook card"""
    tags = json.loads(notebook['tags']) if notebook['tags'] else []
    tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in tags])
    
    # Status color
    analyzed = notebook.get('analyzed', 0)
    status_class = "status-analyzed" if analyzed else "status-pending"
    status_text = "✅ AI Analyzed" if analyzed else "⏳ Pending"
    
    # Account badge
    account = notebook.get('account', 'Unknown')
    
    colab_link = notebook.get('colab_link', '#')
    drive_link = notebook.get('web_link', '#')
    
    st.markdown(f"""
    <div class="notebook-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <div>
                <h3 style="color: #f1f5f9; margin: 0; font-size: 1.3rem;">
                    📓 {notebook['name']}
                </h3>
                <div style="margin-top: 8px;">
                    <span class="tag tag-category">{notebook.get('category', 'Uncategorized')}</span>
                    <span class="tag tag-status-{account.lower()}">{account}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <span class="status-dot {status_class}"></span>
                <span style="color: #94a3b8; font-size: 0.85rem;">{status_text}</span>
            </div>
        </div>
        
        <p style="color: #cbd5e1; margin: 15px 0; line-height: 1.6;">
            {notebook.get('summary', notebook.get('main_goal', 'No summary available'))}
        </p>
        
        <p style="color: #94a3b8; font-size: 0.9rem; margin: 10px 0;">
            <strong style="color: #f1f5f9;">🎯 Goal:</strong> {notebook.get('main_goal', 'Not specified')}
        </p>
        
        <div style="margin: 15px 0;">
            <strong style="color: #94a3b8;">🏷️ Tags:</strong><br>
            {tags_html}
        </div>
        
        <div style="display: flex; gap: 15px; margin-top: 20px; flex-wrap: wrap;">
            <div style="color: #94a3b8; font-size: 0.85rem;">
                <span style="color: #6366f1;">📝</span> {notebook.get('total_code_lines', 0):,} lines
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem;">
                <span style="color: #ec4899;">🕒</span> {notebook.get('modified_time', 'Unknown')[:10]}
            </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <a href="{colab_link}" target="_blank" style="
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                flex: 1;
                text-align: center;
            ">🚀 Open in Colab</a>
            
            <a href="{drive_link}" target="_blank" style="
                background: linear-gradient(135deg, #1e293b, #334155);
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                flex: 1;
                text-align: center;
                border: 1px solid #475569;
            ">📂 View in Drive</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    st.markdown("<h1 class='main-header'>🤖 AI Colab Manager</h1>", unsafe_allow_html=True)
    
    db = NotebookDatabase()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <img src="https://www.gstatic.com/colaboratory/assets/colab-logo.svg" width="80">
            <h2 style="color: #f1f5f9; margin-top: 15px;">Colab Manager</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons
        st.markdown("### 🎯 Quick Actions")
        
        scan_clicked = st.button("🔄 Scan Drive", use_container_width=True)
        
        analyze_clicked = st.button("🧠 Analyze All", use_container_width=True)
        
        if scan_clicked:
            with st.spinner("🔍 Scanning Google Drive..."):
                try:
                    result = subprocess.run(["python", "scanner.py"], 
                                          capture_output=True, text=True, timeout=300)
                    st.success("✅ Scan complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if analyze_clicked:
            with st.spinner("🧠 Analyzing with AI..."):
                try:
                    result = subprocess.run(["python", "agent.py"], 
                                          capture_output=True, text=True, timeout=600)
                    st.success("✅ Analysis complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "🏠 Dashboard": "dashboard",
            "📚 All Notebooks": "notebooks",
            "🔍 Search": "search",
            "📊 Analytics": "analytics",
            "⚙️ Settings": "settings"
        }
        
        selected_page = st.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
        
        st.markdown("---")
        
        # Quick stats
        stats = db.get_statistics()
        st.markdown("### 📈 Quick Stats")
        st.markdown(f"""
        <div class="info-box">
            <p style="color: #f1f5f9; margin: 5px 0;">
                <span class="status-dot status-active"></span>
                Total: {stats['total']}
            </p>
            <p style="color: #f1f5f9; margin: 5px 0;">
                <span class="status-dot status-analyzed"></span>
                Analyzed: {stats['analyzed']}
            </p>
            <p style="color: #f1f5f9; margin: 5px 0;">
                <span style="color: #6366f1;">📝</span>
                Code Lines: {stats['total_lines']:,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content based on page
    page = pages[selected_page]
    
    if page == "dashboard":
        show_dashboard(db)
    elif page == "notebooks":
        show_all_notebooks(db)
    elif page == "search":
        show_search(db)
    elif page == "analytics":
        show_analytics(db)
    elif page == "settings":
        show_settings()


def show_dashboard(db):
    """Main dashboard with beautiful cards"""
    stats = db.get_statistics()
    
    # Hero metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric_card(stats['total'], "Total Notebooks", "📓")
    with col2:
        display_metric_card(stats['analyzed'], "AI Analyzed", "🧠")
    with col3:
        display_metric_card(stats['total'] - stats['analyzed'], "Pending", "⏳")
    with col4:
        display_metric_card(stats['total_lines'], "Lines of Code", "📝")
    
    st.markdown("---")
    
    # Recent notebooks section
    st.markdown('<p class="section-header">🕒 Recently Modified Notebooks</p>', unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 40px;">
            <h3 style="color: #f1f5f9;">👋 Welcome!</h3>
            <p style="color: #94a3b8;">Click "🔄 Scan Drive" in the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display 3 recent notebooks
    recent = df.head(3)
    for _, nb in recent.iterrows():
        display_notebook_card(nb)
    
    # Quick actions
    st.markdown("---")
    st.markdown('<p class="section-header">⚡ Quick Actions</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📓 View All Notebooks", use_container_width=True):
            st.session_state['page'] = 'notebooks'
            st.rerun()
    
    with col2:
        if st.button("🔍 Search Notebooks", use_container_width=True):
            st.session_state['page'] = 'search'
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state['page'] = 'analytics'
            st.rerun()


def show_all_notebooks(db):
    """All notebooks with filters"""
    st.markdown('<p class="section-header">📚 All Notebooks</p>', unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.info("No notebooks found. Click 'Scan Drive' in the sidebar.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(df['category'].dropna().unique().tolist())
        selected_cat = st.selectbox("📁 Category", categories)
    
    with col2:
        accounts = ['All'] + sorted(df['account'].unique().tolist())
        selected_account = st.selectbox("👤 Account", accounts)
    
    with col3:
        analyzed_filter = st.selectbox("📊 Status", ["All", "Analyzed", "Pending"])
    
    # Filter data
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_account != 'All':
        filtered = filtered[filtered['account'] == selected_account]
    
    if analyzed_filter == "Analyzed":
        filtered = filtered[filtered['analyzed'] == 1]
    elif analyzed_filter == "Pending":
        filtered = filtered[filtered['analyzed'] == 0]
    
    st.markdown(f"### Showing {len(filtered)} of {len(df)} notebooks")
    
    # Display all filtered notebooks
    for _, nb in filtered.iterrows():
        display_notebook_card(nb)


def show_search(db):
    """Search functionality"""
    st.markdown('<p class="section-header">🔍 Search Notebooks</p>', unsafe_allow_html=True)
    
    search_term = st.text_input(
        "What are you looking for?",
        placeholder="e.g., 'machine learning', 'tensorflow', 'image classification', 'nlp'...",
        label_visibility="collapsed"
    )
    
    if search_term:
        results = db.search_notebooks(search_term)
        
        st.markdown(f"### Found {len(results)} results for '{search_term}'")
        
        if results.empty:
            st.markdown("""
            <div class="info-box">
                <p style="color: #94a3b8; text-align: center;">No results found. Try different keywords.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for _, nb in results.iterrows():
                display_notebook_card(nb)
    else:
        # Suggested searches
        st.markdown("### 💡 Try searching for:")
        
        col1, col2, col3 = st.columns(3)
        
        suggestions = [
            ("Machine Learning", "machine learning"),
            ("Deep Learning", "deep learning"),
            ("Data Analysis", "data analysis"),
            ("NLP", "nlp, natural language"),
            ("Computer Vision", "vision, image"),
            ("TensorFlow", "tensorflow"),
            ("PyTorch", "pytorch"),
            ("Research", "research"),
            ("Experiment", "experiment")
        ]
        
        for i, (label, term) in enumerate(suggestions):
            col = i % 3
            if i < 3:
                with col1:
                    if st.button(f"🔍 {label}"):
                        st.session_state['search_term'] = term
                        st.rerun()
            elif i < 6:
                with col2:
                    if st.button(f"🔍 {label}"):
                        st.session_state['search_term'] = term
                        st.rerun()
            else:
                with col3:
                    if st.button(f"🔍 {label}"):
                        st.session_state['search_term'] = term
                        st.rerun()


def show_analytics(db):
    """Analytics with charts"""
    st.markdown('<p class="section-header">📊 Analytics Dashboard</p>', unsafe_allow_html=True)
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.warning("No data available. Scan your notebooks first.")
        return
    
    stats = db.get_statistics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric_card(len(df), "Total", "📓")
    with col2:
        display_metric_card(len(df[df['category'] == 'Machine Learning']), "ML", "🤖")
    with col3:
        display_metric_card(len(df[df['category'] == 'Deep Learning']), "DL", "🧠")
    with col4:
        display_metric_card(stats['total_lines'], "Code Lines", "📝")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📂 Category Distribution")
        
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
                legend=dict(color='#f1f5f9')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 👤 Account Distribution")
        
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
    st.markdown("### 🏷️ Most Used Technologies")
    
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


def show_settings():
    """Settings page"""
    st.markdown('<p class="section-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    # API Status
    st.markdown("### 🔑 API Status")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        st.success(f"✅ Gemini API Key configured ({api_key[:15]}...)")
    else:
        st.error("❌ Gemini API Key not found")
        st.info("Add your API key to the .env file: GEMINI_API_KEY=your_key")
    
    st.markdown("---")
    
    # Files
    st.markdown("### 📁 File Status")
    
    files_to_check = [
        ("Database", "database.db"),
        ("Scanner", "scanner.py"),
        ("Agent", "agent.py"),
        ("App", "app.py")
    ]
    
    for name, filepath in files_to_check:
        exists = os.path.exists(filepath)
        status = "✅ Found" if exists else "❌ Missing"
        color = "success" if exists else "error"
        
        if exists:
            size = os.path.getsize(filepath)
            st.markdown(f"- **{name}**: {status} ({size:,} bytes)")
        else:
            st.markdown(f"- **{name}**: {status}")
    
    st.markdown("---")
    
    # Help
    st.markdown("### 📖 Help")
    
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Quick Start:**
        1. Click **"🔄 Scan Drive"** to scan your Colab notebooks
        2. Click **"🧠 Analyze All"** to generate AI insights
        3. Browse and search your notebooks here
        
        **Automation:**
        - Set up Windows Task Scheduler for automatic daily scans
        - Or run scripts manually from your terminal
        
        **Searching:**
        - Use keywords like 'machine learning', 'tensorflow', 'nlp'
        - Search by category, tags, or notebook name
        """)
    
    with st.expander("🐛 Troubleshooting"):
        st.markdown("""
        **Issue: No notebooks found**
        - Make sure you have service account credentials set up
        - Check that you've shared your Drive folders with the service account
        
        **Issue: Analysis failing**
        - Check your Gemini API key is valid
        - Make sure you have internet connection
        
        **Issue: App not loading**
        - Refresh the page
        - Check if database.db exists
        """)


if __name__ == "__main__":
    main()
