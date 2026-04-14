"""
Beautiful Streamlit Dashboard for Colab Notebook Manager
Fixed UI with better error handling and beautiful design
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
import sys

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# In agent.py or when using API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.getenv('GEMINI_API_KEY')

# Beautiful CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content area */
    .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    /* Header */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Metric boxes */
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s;
        margin: 10px 0;
    }
    
    .metric-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    .metric-box h2 {
        font-size: 3rem;
        margin: 0;
        font-weight: bold;
    }
    
    .metric-box p {
        font-size: 1.2rem;
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    /* Notebook cards */
    .notebook-card {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        transition: all 0.3s;
        cursor: pointer;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .notebook-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        border-color: #667eea;
    }
    
    .notebook-card h3 {
        color: #333;
        margin-top: 0;
        font-size: 1.5rem;
    }
    
    /* Tags */
    .tag {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 5px solid #2196F3;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .success-box {
        background: #e8f5e9;
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .warning-box {
        background: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Database class
class NotebookDatabase:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.ensure_database_exists()
        
    def ensure_database_exists(self):
        """Create database and table if they don't exist"""
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
            st.error(f"Database error: {e}")
    
    def get_all_notebooks(self):
        """Get all notebooks from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT * FROM notebooks ORDER BY modified_time DESC"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading notebooks: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get summary statistics"""
        try:
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
            st.error(f"Error getting statistics: {e}")
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
            st.error(f"Search error: {e}")
            return pd.DataFrame()

def display_notebook_card(notebook):
    """Display a beautiful notebook card"""
    try:
        tags = json.loads(notebook['tags']) if notebook['tags'] and notebook['tags'] != 'null' else []
    except:
        tags = []
    
    tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in tags[:5]])
    
    st.markdown(f"""
    <div class='notebook-card'>
        <h3>📓 {notebook['name']}</h3>
        <p><strong>👤 Account:</strong> {notebook['account']}</p>
        <p><strong>📁 Category:</strong> {notebook['category'] or 'Uncategorized'}</p>
        <p><strong>📝 Summary:</strong> {notebook['summary'] or 'Not analyzed yet'}</p>
        <p><strong>🎯 Goal:</strong> {notebook['main_goal'] or 'Not specified'}</p>
        <p><strong>💡 Key Findings:</strong> {notebook['key_findings'] or 'N/A'}</p>
        <p><strong>📊 Code Lines:</strong> {notebook['total_code_lines']:,}</p>
        <p><strong>🏷️ Tags:</strong><br>{tags_html if tags_html else '<em>No tags</em>'}</p>
        <p><small>🕒 Modified: {notebook['modified_time'][:10] if notebook['modified_time'] else 'Unknown'}</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if notebook['colab_link']:
            st.link_button("🚀 Open in Colab", notebook['colab_link'], use_container_width=True)
    with col2:
        if notebook['web_link']:
            st.link_button("📂 Open in Drive", notebook['web_link'], use_container_width=True)

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI-Powered Colab Manager</h1>", unsafe_allow_html=True)
    
    # Initialize database
    db = NotebookDatabase()
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.gstatic.com/colaboratory/assets/colab-logo.svg", width=150)
        st.title("⚙️ Control Panel")
        
        st.markdown("---")
        
        # Action buttons
        st.subheader("🔧 Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Scan Drive", use_container_width=True, help="Scan Google Drive for notebooks"):
                with st.spinner("Scanning..."):
                    try:
                        result = subprocess.run(
                            [sys.executable, "scanner.py"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            st.success("✅ Scan complete!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        st.error("Scan timed out")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col2:
            if st.button("🧠 Analyze", use_container_width=True, help="Analyze notebooks with AI"):
                with st.spinner("Analyzing..."):
                    try:
                        result = subprocess.run(
                            [sys.executable, "agent.py"],
                            capture_output=True,
                            text=True,
                            timeout=600
                        )
                        if result.returncode == 0:
                            st.success("✅ Analysis complete!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        st.error("Analysis timed out")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("📍 Navigation")
        page = st.radio(
            "Go to:",
            ["🏠 Dashboard", "📚 All Notebooks", "🔍 Search", "📊 Analytics", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        stats = db.get_statistics()
        
        st.metric("Total Notebooks", stats['total'])
        st.metric("Analyzed", stats['analyzed'])
        st.metric("Code Lines", f"{stats['total_lines']:,}")
        
        # Progress
        if stats['total'] > 0:
            progress = stats['analyzed'] / stats['total']
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
    elif page == "⚙️ Settings":
        show_settings()

def show_welcome_screen():
    """Welcome screen when no data"""
    st.markdown("""
    <div class='info-box'>
        <h2>👋 Welcome to AI Colab Manager!</h2>
        <p>Get started by scanning your Google Drive for Colab notebooks.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Quick Start
        
        1. **Click "🔄 Scan Drive"** in the sidebar
        2. Login to your Google account
        3. Wait for the scan to complete
        4. **Click "🧠 Analyze"** to get AI insights
        5. Explore your notebooks!
        
        ### ✨ Features
        
        - 📊 AI-powered analysis
        - 🔍 Smart search
        - 📈 Analytics dashboard
        - 🏷️ Automatic tagging
        - 🎯 Category detection
        """)
    
    with col2:
        st.markdown("""
        ### 📋 Requirements
        
        ✅ Google account with Colab notebooks  
        ✅ Google Drive API enabled  
        ✅ Gemini API key configured  
        ✅ Internet connection
        
        ### 🆘 Need Help?
        
        - Check `credentials.json` is in folder
        - Verify `.env` has `GEMINI_API_KEY`
        - Make sure Python packages are installed
        - Run `python scanner.py Account1` manually to test
        """)
    
    # Show files status
    st.markdown("---")
    st.subheader("📁 File Check")
    
    files_to_check = {
        'credentials.json': '🔑 Google OAuth credentials',
        '.env': '🔐 API keys',
        'scanner.py': '📡 Drive scanner script',
        'agent.py': '🤖 AI analyzer script',
        'database.db': '💾 Database (created after first scan)'
    }
    
    cols = st.columns(3)
    for i, (file, desc) in enumerate(files_to_check.items()):
        with cols[i % 3]:
            if os.path.exists(file):
                st.success(f"✅ {file}")
            else:
                st.error(f"❌ {file}")
            st.caption(desc)

def show_dashboard(db, stats):
    """Main dashboard"""
    st.header("📊 Dashboard Overview")
    
    # Metrics row
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
    
    # Recent notebooks
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕒 Recently Modified")
        df = db.get_all_notebooks()
        if not df.empty:
            recent = df.head(5)
            for _, nb in recent.iterrows():
                display_notebook_card(nb)
        else:
            st.info("No notebooks yet")
    
    with col2:
        st.subheader("📁 By Category")
        if stats['by_category']:
            fig = px.pie(
                values=list(stats['by_category'].values()),
                names=list(stats['by_category'].keys()),
                color_discrete_sequence=px.colors.sequential.Purples
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categories yet - run AI analysis")

def show_all_notebooks(db):
    """Show all notebooks"""
    st.header("📚 All Notebooks")
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.warning("No notebooks found. Click 'Scan Drive' in the sidebar.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted([c for c in df['category'].dropna().unique() if c])
        selected_cat = st.selectbox("📁 Category", categories)
    
    with col2:
        accounts = ['All'] + sorted(df['account'].unique().tolist())
        selected_account = st.selectbox("👤 Account", accounts)
    
    with col3:
        sort_by = st.selectbox("🔀 Sort by", ["Recent", "Name", "Size"])
    
    # Filter
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
    
    st.info(f"📊 Showing {len(filtered)} of {len(df)} notebooks")
    
    # Display
    for _, nb in filtered.iterrows():
        display_notebook_card(nb)

def show_search(db):
    """Search page"""
    st.header("🔍 Search Notebooks")
    
    search_term = st.text_input(
        "🔎 Search",
        placeholder="Enter keywords, tags, or category...",
        help="Search in name, summary, tags, and category"
    )
    
    if search_term:
        results = db.search_notebooks(search_term)
        
        if not results.empty:
            st.success(f"✅ Found {len(results)} results for '{search_term}'")
            
            for _, nb in results.iterrows():
                display_notebook_card(nb)
        else:
            st.warning(f"No results found for '{search_term}'")
    else:
        st.info("👆 Enter a search term above")

def show_analytics(db):
    """Analytics page"""
    st.header("📊 Analytics & Insights")
    
    df = db.get_all_notebooks()
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Category distribution
    if 'category' in df.columns:
        st.subheader("📂 Notebooks by Category")
        category_counts = df['category'].value_counts()
        
        if not category_counts.empty:
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Distribution by Category",
                color_discrete_sequence=px.colors.sequential.Purples
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    if 'created_time' in df.columns:
        st.subheader("📈 Creation Timeline")
        df['created_date'] = pd.to_datetime(df['created_time'], errors='coerce').dt.date
        timeline = df.groupby('created_date').size().reset_index(name='count')
        timeline = timeline.dropna()
        
        if not timeline.empty:
            fig = px.line(
                timeline,
                x='created_date',
                y='count',
                title="Notebooks Created Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Account distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 By Account")
        account_counts = df['account'].value_counts()
        fig = px.bar(
            x=account_counts.index,
            y=account_counts.values,
            labels={'x': 'Account', 'y': 'Count'},
            color=account_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Code Size")
        fig = px.histogram(
            df,
            x='total_code_lines',
            nbins=20,
            title="Lines of Code Distribution",
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Popular tags
    st.subheader("🏷️ Most Used Tags")
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
            title="Top 20 Tags",
            labels={'x': 'Count', 'y': 'Tag'},
            color=tag_counts.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tags found - run AI analysis first")

def show_settings():
    """Settings page"""
    st.header("⚙️ Settings")
    
    # API Status
    st.subheader("🔑 API Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        st.success(f"✅ Gemini API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        st.error("❌ Gemini API Key not found")
        st.code("Add to .env file:\nGEMINI_API_KEY=your_key_here")
    
    # Google Drive Accounts
    st.markdown("---")
    st.subheader("📂 Google Drive Accounts")
    
    token_files = [f for f in os.listdir('.') if f.startswith('token_') and f.endswith('.pickle')]
    
    if token_files:
        for token_file in token_files:
            account_name = token_file.replace('token_', '').replace('.pickle', '')
            
            # Check if email file exists
            email_file = f'{account_name}_email.txt'
            if os.path.exists(email_file):
                with open(email_file, 'r') as f:
                    email = f.read().strip()
                st.success(f"✅ {account_name}: {email}")
            else:
                st.success(f"✅ {account_name} authenticated")
    else:
        st.warning("⚠️ No accounts authenticated yet")
        st.info("Run: python scanner.py Account1")
    
    # Database Info
    st.markdown("---")
    st.subheader("🗄️ Database Information")
    
    if os.path.exists('database.db'):
        size = os.path.getsize('database.db') / 1024 / 1024
        st.info(f"📊 Database size: {size:.2f} MB")
        
        # Show table info
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notebooks")
        count = cursor.fetchone()[0]
        conn.close()
        
        st.info(f"📓 Total records: {count}")
        
        # Refresh button
        if st.button("🔄 Rebuild Database", help="Recreate database tables"):
            db = NotebookDatabase()
            db.ensure_database_exists()
            st.success("✅ Database refreshed!")
    else:
        st.warning("⚠️ Database not created yet")
        st.info("Run a scan to create the database")
    
    # System Info
    st.markdown("---")
    st.subheader("💻 System Information")
    
    st.info(f"🐍 Python: {sys.version.split()[0]}")
    st.info(f"📁 Working Directory: {os.getcwd()}")
    
    # Clear cache
    if st.button("🗑️ Clear Streamlit Cache"):
        st.cache_data.clear()
        st.success("✅ Cache cleared!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.code(f"{type(e).__name__}: {str(e)}")
        
        with st.expander("🔍 Debug Information"):
            import traceback
            st.code(traceback.format_exc())
