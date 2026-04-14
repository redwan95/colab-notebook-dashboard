"""
AI-Powered Colab Notebook Manager
Fully Functional - Auto-sync & Manual Upload
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DARK THEME CSS - GitHub Style
# ============================================
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main background - GitHub dark */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* All text */
    html, body, p, span, div {
        color: #c9d1d9 !important;
    }
    
    /* Headers - Blue accent */
    h1 { color: #58a6ff !important; }
    h2 { color: #f0f6fc !important; }
    h3 { color: #f0f6fc !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #58a6ff;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-top: 8px;
    }
    
    /* Cards */
    .notebook-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .card-title {
        color: #f0f6fc !important;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    .card-text {
        color: #8b949e;
        line-height: 1.6;
    }
    
    /* Tags */
    .tag {
        background-color: #1f6feb;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 3px;
        display: inline-block;
    }
    
    .tag-cat { background-color: #a371f7; }
    .tag-acc { background-color: #238636; }
    .tag-analyzed { background-color: #238636; }
    .tag-pending { background-color: #f0883e; }
    
    /* Navigation tabs */
    .nav-tab {
        background-color: #21262d;
        border-radius: 6px;
        padding: 10px 15px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-tab:hover {
        background-color: #30363d;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
    }
    
    .btn-secondary > button {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
    }
    
    .btn-link > button {
        background-color: #0969da !important;
    }
    
    /* Links styling */
    a {
        color: #58a6ff !important;
        text-decoration: none;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px;
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        background-color: #0d1117 !important;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #161b22;
        border-left: 4px solid #58a6ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Upload box */
    .upload-box {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 2px dashed #30363d;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #30363d;
        margin: 25px 0;
    }
    
    /* Tables */
    .dataframe {
        background-color: #161b22 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #21262d;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================
def init_database():
    """Initialize database and tables"""
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


def load_database(db_path):
    """Load database from file"""
    try:
        if not os.path.exists(db_path):
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM notebooks ORDER BY modified_time DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()


def save_uploaded_db(uploaded_file):
    """Save uploaded database file"""
    try:
        # Read uploaded file
        bytes_data = uploaded_file.read()
        
        # Save to local database.db
        with open('database.db', 'wb') as f:
            f.write(bytes_data)
        
        return True
    except Exception as e:
        st.error(f"Error saving database: {e}")
        return False


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
    stats['lines'] = int(df['total_code_lines'].sum()) if 'total_code_lines' in df.columns else 0
    
    if 'category' in df.columns:
        cats = df['category'].value_counts().to_dict()
        stats['categories'] = {k: v for k, v in cats.items() if k and pd.notna(k)}
