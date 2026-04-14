"""
AI-Powered Colab Notebook Manager
✅ Clickable buttons that work
✅ Auto-sync database
✅ Manual upload option
✅ Beautiful, functional UI
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="🤖 AI Colab Manager",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ENHANCED CSS - DARK THEME WITH WORKING LINKS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    html, body, [class*="css"] {
        color: #c9d1d9;
    }
    
    h1, h2, h3, h4 {
        color: #58a6ff !important;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
        margin-bottom: 10px;
    }
    
    .subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #58a6ff;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(88, 166, 255, 0.2);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    
    .notebook-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .notebook-card:hover {
        border-color: #58a6ff;
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(88, 166, 255, 0.15);
    }
    
    .notebook-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(180deg, #58a6ff, #bc8cff);
        border-radius: 16px 0 0 16px;
    }
    
    .notebook-title {
        color: #f0f6fc;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .tag {
        background: linear-gradient(135deg, #388bfd, #5b4cdb);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 4px;
        display: inline-block;
        font-weight: 500;
    }
    
    .tag-category {
        background: linear-gradient(135deg, #a371f7, #e96df5);
    }
    
    .tag-account {
        background: linear-gradient(135deg, #56d364, #2ea043);
    }
    
    .status-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-analyzed {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #f0883e, #db6d28);
        color: white;
    }
    
    .action-button {
        display: inline-block;
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white !important;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .action-button:hover {
        background: linear-gradient(135deg, #2ea043, #3fb950);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 160, 67, 0.4);
        color: white !important;
    }
    
    .action-button-secondary {
        background: linear-gradient(135deg, #1f6feb, #388bfd);
    }
    
    .action-button-secondary:hover {
        background: linear-gradient(135deg, #388bfd, #58a6ff);
        box-shadow: 0 5px 15px rgba(56, 139, 253, 0.4);
    }
    
    .info-box {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border-left: 4px solid #58a6ff;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }
    
    .upload-box {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border: 2px dashed #30363d;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #58a6ff;
        background: linear-gradient(135deg, #1c2128, #161b22);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043, #3fb950);
        transform: translateY(-2px);
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #0d1117;
    }
    
    .divider {
        border-top: 1px solid #30363d;
        margin: 30px 0;
    }
    
    .streamlit-expanderHeader {
        background-color: #161b22;
        border-radius: 10px;
        color: #f0f6fc;
    }
    
    .success-box {
        background: linear-gradient(135deg, #0d4d28, #0f5132);
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 4px solid #2ea043;
        margin: 10px 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #4d3800, #5c4200);
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 4px solid #f0883e;
        margin: 10px 0;
    }
    
    a {
        color: #58a6ff !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #79c0ff !important;
        text-decoration: underline !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================
def init_db(db_path='database.db'):
    """Initialize database"""
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


def load_database(db_path='database.db'):
    """Load data from database"""
    if not os.path.exists(db_path):
        return pd.DataFrame(), {}
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM notebooks ORDER BY modified_time DESC", conn)
        conn.close()
        
        stats = calculate_stats(df)
        return df, stats
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame(), {}


def calculate_stats(df):
    """Calculate statistics"""
    stats = {
        'total': 0,
        'analyzed': 0,
        'pending': 0,
        'lines': 0,
        'categories': {},
        'accounts': {},
        'last_updated': 'Never'
    }
    
    if df.empty:
        return stats
    
    stats['total'] = len(df)
    stats['analyzed'] = len(df[df['analyzed'] == 1]) if 'analyzed' in df.columns else 0
    stats['pending'] = stats['total'] - stats['analyzed']
    stats['lines'] = int(df['total_code_lines'].sum()) if 'total_code_lines' in df.columns else 0
    
    if 'category' in df.columns:
        cats = df['category'].value_counts().to_dict()
        stats['categories'] = {k: v for k, v in cats.items() if k and str(k) != 'nan'}
    
    if 'account' in df.columns:
        accs = df['account'].value_counts().to_dict()
        stats['accounts'] = {k: v for k, v in accs.items() if k and str(k) != 'nan'}
    
    if 'scanned_at' in df.columns and not df['scanned_at'].empty:
        latest = df['scanned_at'].max()
        if latest:
            stats['last_updated'] = str(latest)[:19]
    
    return stats


def save_uploaded_database(uploaded_file):
    """Save uploaded database file"""
    try:
        # Save the uploaded file
        with open('database.db', 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Error saving database: {e}")
        return False


# ============================================
# DISPLAY COMPONENTS
# ============================================
def show_metric(value, label, icon="📊"):
    """Show metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2.5rem; margin-bottom: 10px;">{icon}</div>
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def show_notebook_card(nb):
    """Display notebook with reinforced rendering and fallback logic"""
    
    # 1. Extract Data
    name = str(nb.get('name', 'Unnamed Notebook'))
    category = str(nb.get('category', 'General'))
    account = str(nb.get('account', 'Default'))
    
    # The "Summary" often comes from the 'summary' column, fallback to 'main_goal'
    raw_summary = nb.get('summary')
    if not raw_summary or str(raw_summary).strip() == "" or str(raw_summary) == "None":
        raw_summary = nb.get('main_goal', "⚠️ No AI analysis found. Please run agent.py.")
    
    summary_content = str(raw_summary)
    
    # 2. Extract Technical Stats
    lines = int(nb.get('total_code_lines', 0) or 0)
    modified = str(nb.get('modified_time', 'Unknown'))[:10]
    colab_link = str(nb.get('colab_link', '#'))
    drive_link = str(nb.get('web_link', '#'))
    analyzed = int(nb.get('analyzed', 0))
    
    status_html = f'<span class="status-badge status-analyzed">✅ AI Analyzed</span>' if analyzed else f'<span class="status-badge status-pending">⏳ Pending</span>'

    # 3. The Layout (Single HTML block to prevent Streamlit Markdown interference)
    st.markdown(f"""
    <div class="notebook-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <div style="flex: 1;">
                <h3 class="notebook-title" style="margin: 0; color: #58a6ff;">📓 {name}</h3>
                <div style="margin-top: 10px;">
                    <span class="tag tag-category">{category}</span>
                    <span class="tag tag-account">{account}</span>
                    {status_html}
                </div>
            </div>
        </div>
        
        <div class="summary-box" style="background: rgba(48, 54, 61, 0.2); border-radius: 8px; padding: 15px; margin: 15px 0; border: 1px solid #30363d;">
            <div style="color: #c9d1d9; font-size: 0.95rem; line-height: 1.6;">
                {summary_content}
            </div>
        </div>
        
        <div style="display: flex; gap: 20px; color: #6e7681; font-size: 0.85rem; margin-top: 10px;">
            <span>📝 {lines:,} Code Lines</span>
            <span>🕒 Last Modified: {modified}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4. Interactive Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🚀 Open in Colab", colab_link, use_container_width=True)
    with col2:
        if drive_link != '#':
            st.link_button("📂 View in Drive", drive_link, use_container_width=True)

# ============================================
# MAIN APP
# ============================================
def main():
    """Main application"""
    
    # Initialize database
    init_db()
    
    # Header
    st.markdown("<h1 class='main-title'>🤖 AI Colab Notebook Manager</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Intelligent organization for your Google Colab projects</p>", unsafe_allow_html=True)
    
    # Load data
    df, stats = load_database()
    
    # ============================================
    # SIDEBAR
    # ============================================
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 15px;">
            <img src="https://www.gstatic.com/colaboratory/assets/colab-logo.svg" width="70">
            <h2 style="color: #58a6ff; margin-top: 15px; font-size: 1.4rem;">Colab Manager</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Database upload section
        st.markdown("### 📤 Upload Database")
        
        uploaded_file = st.file_uploader(
            "Upload database.db",
            type=['db'],
            help="Upload your database.db file generated by scanner.py and agent.py",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            if st.button("💾 Save & Reload", use_container_width=True):
                with st.spinner("Uploading database..."):
                    if save_uploaded_database(uploaded_file):
                        st.success("✅ Database uploaded successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Upload failed")
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        
        st.markdown(f"""
        <div class="info-box">
            <p style="margin: 8px 0; color: #c9d1d9;">
                <strong>📓 Total:</strong> {stats['total']}
            </p>
            <p style="margin: 8px 0; color: #c9d1d9;">
                <strong>✅ Analyzed:</strong> {stats['analyzed']}
            </p>
            <p style="margin: 8px 0; color: #c9d1d9;">
                <strong>⏳ Pending:</strong> {stats['pending']}
            </p>
            <p style="margin: 8px 0; color: #c9d1d9;">
                <strong>📝 Lines:</strong> {stats['lines']:,}
            </p>
            <p style="margin: 8px 0; color: #6e7681; font-size: 0.85rem;">
                Last Updated: {stats['last_updated'][:10]}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📂 Navigation")
        page = st.radio(
            "Select Page",
            [
                "🏠 Dashboard",
                "📚 All Notebooks",
                "🔍 Search",
                "📊 Analytics",
                "❓ Help"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Instructions
        with st.expander("ℹ️ How to Update"):
            st.markdown("""
            **To update your notebooks:**
            
            1. Run locally:
               ```
               python scanner.py
               python agent.py
               ```
            
            2. Upload the new `database.db` file above
            
            3. Click "Save & Reload"
            """)
    
    # ============================================
    # PAGES
    # ============================================
    
    if page == "🏠 Dashboard":
        show_dashboard(df, stats)
    elif page == "📚 All Notebooks":
        show_all_notebooks(df)
    elif page == "🔍 Search":
        show_search(df)
    elif page == "📊 Analytics":
        show_analytics(stats, df)
    elif page == "❓ Help":
        show_help()


# ============================================
# PAGES
# ============================================
def show_dashboard(df, stats):
    """Dashboard page"""
    
    st.header("📊 Dashboard Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_metric(stats['total'], "Total Notebooks", "📓")
    with col2:
        show_metric(stats['analyzed'], "AI Analyzed", "🧠")
    with col3:
        show_metric(stats['pending'], "Pending Analysis", "⏳")
    with col4:
        show_metric(stats['lines'], "Lines of Code", "📝")
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Recent notebooks
    if df.empty:
        st.markdown("""
        <div class="upload-box">
            <h3 style="color: #58a6ff; margin-bottom: 15px;">👋 Welcome to Colab Manager!</h3>
            <p style="color: #8b949e; margin-bottom: 20px;">
                Get started by uploading your database file
            </p>
            <p style="color: #6e7681; font-size: 0.9rem;">
                1. Run <code>scanner.py</code> locally to scan your notebooks<br>
                2. Run <code>agent.py</code> to analyze with AI<br>
                3. Upload the generated <code>database.db</code> file using the sidebar
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.header("🕒 Recent Notebooks")
        
        # Show 5 most recent
        for _, nb in df.head(5).iterrows():
            show_notebook_card(nb)
        
        # Categories overview
        if stats['categories']:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.header("📂 Categories Overview")
            
            cols = st.columns(min(4, len(stats['categories'])))
            
            for i, (cat, count) in enumerate(list(stats['categories'].items())[:4]):
                with cols[i]:
                    show_metric(count, cat, "📁")


def show_all_notebooks(df):
    """All notebooks page"""
    
    st.header("📚 All Notebooks")
    
    if df.empty:
        st.warning("⚠️ No notebooks found. Upload database.db in the sidebar.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted([c for c in df['category'].dropna().unique() if c and str(c) != 'nan'])
        selected_cat = st.selectbox("📁 Category", categories)
    
    with col2:
        accounts = ['All'] + sorted([a for a in df['account'].dropna().unique() if a and str(a) != 'nan'])
        selected_acc = st.selectbox("👤 Account", accounts)
    
    with col3:
        status_options = ["All", "✅ Analyzed", "⏳ Pending"]
        selected_status = st.selectbox("📊 Status", status_options)
    
    # Apply filters
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_acc != 'All':
        filtered = filtered[filtered['account'] == selected_acc]
    
    if selected_status == "✅ Analyzed":
        filtered = filtered[filtered['analyzed'] == 1]
    elif selected_status == "⏳ Pending":
        filtered = filtered[filtered['analyzed'] == 0]
    
    # Results count
    st.markdown(f"""
    <div class="info-box">
        <p style="color: #c9d1d9; margin: 0;">
            Showing <strong>{len(filtered)}</strong> of <strong>{len(df)}</strong> notebooks
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display notebooks
    for _, nb in filtered.iterrows():
        show_notebook_card(nb)


def show_search(df):
    """Search page"""
    
    st.header("🔍 Search Notebooks")
    
    # Search input
    search_term = st.text_input(
        "Search",
        placeholder="Search by name, category, tags, or summary...",
        label_visibility="collapsed"
    )
    
    if search_term:
        # Search in multiple fields
        term = search_term.lower()
        
        results = df[
            df['name'].str.lower().str.contains(term, na=False) |
            df['summary'].str.lower().str.contains(term, na=False) |
            df['category'].str.lower().str.contains(term, na=False) |
            df['tags'].str.lower().str.contains(term, na=False)
        ]
        
        if results.empty:
            st.markdown(f"""
            <div class="warning-box">
                <p style="color: #f0f6fc; margin: 0;">
                    No results found for "<strong>{search_term}</strong>"
                </p>
                <p style="color: #8b949e; margin-top: 5px; font-size: 0.9rem;">
                    Try different keywords or check your spelling
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-box">
                <p style="color: #f0f6fc; margin: 0;">
                    Found <strong>{len(results)}</strong> results for "<strong>{search_term}</strong>"
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            for _, nb in results.iterrows():
                show_notebook_card(nb)
    else:
        # Quick search suggestions
        st.markdown("### 💡 Quick Search Suggestions")
        
        suggestions = [
            ("🤖 Machine Learning", "machine learning"),
            ("🧠 Deep Learning", "deep learning"),
            ("💬 NLP", "nlp"),
            ("🔥 TensorFlow", "tensorflow"),
            ("⚡ PyTorch", "pytorch"),
            ("📊 Data Analysis", "data"),
            ("👁️ Computer Vision", "vision"),
            ("🔬 Research", "research"),
        ]
        
        cols = st.columns(4)
        
        for i, (label, term) in enumerate(suggestions):
            with cols[i % 4]:
                if st.button(label, key=f"search_{i}", use_container_width=True):
                    st.session_state['search_term'] = term
                    st.rerun()


def show_analytics(stats, df):
    """Analytics page"""
    
    st.header("📊 Analytics & Insights")
    
    if df.empty:
        st.warning("⚠️ No data available. Upload database first.")
        return
    
    # Top metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_metric(stats['total'], "Total Notebooks", "📓")
    with col2:
        show_metric(stats['lines'], "Total Code Lines", "📝")
    with col3:
        show_metric(len(stats['categories']), "Categories", "📁")
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 By Category")
        
        if stats['categories']:
            import plotly.express as px
            
            fig = px.pie(
                names=list(stats['categories'].keys()),
                values=list(stats['categories'].values()),
                title="Distribution by Category",
                hole=0.4
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                legend=dict(font_color='#c9d1d9')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👤 By Account")
        
        if stats['accounts']:
            import plotly.express as px
            
            fig = px.bar(
                x=list(stats['accounts'].keys()),
                y=list(stats['accounts'].values()),
                title="Notebooks per Account"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                xaxis_title="Account",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Technologies
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.subheader("🏷️ Most Used Technologies")
    
    all_tags = []
    for tags_str in df['tags'].dropna():
        try:
            tags = json.loads(tags_str) if isinstance(tags_str, str) else tags_str
            all_tags.extend(tags)
        except:
            pass
    
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags).most_common(20)
        
        tags_df = pd.DataFrame(tag_counts, columns=['Technology', 'Count'])
        
        import plotly.express as px
        
        fig = px.bar(
            tags_df,
            x='Count',
            y='Technology',
            orientation='h',
            title="Top 20 Technologies"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_help():
    """Help page"""
    
    st.header("❓ Help & Setup Guide")
    
    with st.expander("🚀 Quick Start Guide", expanded=True):
        st.markdown("""
        ### Getting Started
        
        **Step 1: Set up locally**
        ```bash
        # Install dependencies
        pip install -r requirements.txt
        ```
        
        **Step 2: Scan your notebooks**
        ```bash
        python scanner.py
        ```
        This scans your Google Drive for all Colab notebooks.
        
        **Step 3: Analyze with AI**
        ```bash
        python agent.py
        ```
        This uses Google Gemini AI to analyze and categorize your notebooks.
        
        **Step 4: Upload database**
        - Find the `database.db` file in your project folder
        - Upload it using the sidebar file uploader
        - Click "Save & Reload"
        
        **Step 5: Enjoy!**
        - Browse your notebooks
        - Search by keywords
        - Click to open in Colab
        """)
    
    with st.expander("📤 How to Update Data"):
        st.markdown("""
        ### Updating Your Notebooks
        
        **When you have new notebooks:**
        
        1. Run the scanner again:
           ```
           python scanner.py
           ```
        
        2. Run the analyzer:
           ```
           python agent.py
           ```
        
        3. Upload the new `database.db` file
        
        4. Click "Save & Reload"
        
        **Auto-sync coming soon!** We're working on automatic syncing.
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        ### Common Issues
        
        **Q: Upload button not working**
        - Make sure you selected a `.db` file
        - File must be named `database.db`
        - Try refreshing the page
        
        **Q: No notebooks showing**
        - Check if database.db has data
        - Run scanner.py and agent.py first
        - Make sure upload was successful
        
        **Q: Links not working**
        - Links open in new tabs
        - Make sure you're logged into Google
        - Check if notebook still exists in Drive
        
        **Q: How to run locally?**
        ```
        streamlit run app.py
        ```
        Then open http://localhost:8501
        """)
    
    with st.expander("📁 File Structure"):
        st.markdown("""
        ### Project Structure
        
        ```
        colab-analyzer/
        ├── app.py              ← This dashboard
        ├── scanner.py         ← Scans Google Drive
        ├── agent.py           ← AI analysis
        ├── requirements.txt   ← Dependencies
        ├── database.db        ← Your data (upload this)
        ├── .env               ← API keys (local only)
        └── .streamlit/
            └── config.toml    ← Theme config
        ```
        """)
    
    with st.expander("🔑 API Setup"):
        st.markdown("""
        ### Setting Up APIs
        
        **Google Gemini API:**
        1. Go to https://aistudio.google.com/app/apikey
        2. Click "Create API Key"
        3. Copy the key
        4. Add to `.env`: `GEMINI_API_KEY=your_key`
        
        **Google Drive API:**
        1. Go to https://console.cloud.google.com/
        2. Create a service account
        3. Download JSON credentials
        4. Share your Drive folders with service account email
        """)


# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    main()
