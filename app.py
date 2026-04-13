import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="📓 My Colab Notebooks",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .notebook-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
    }
    .priority-high { border-left: 5px solid #ff4444; }
    .priority-medium { border-left: 5px solid #ffaa00; }
    .priority-low { border-left: 5px solid #44ff44; }
    .tag {
        background: #667eea;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 2px;
        display: inline-block;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def load_data(uploaded_file):
    """Load JSON data from uploaded file"""
    try:
        data = json.load(uploaded_file)
        return data
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def display_notebook_card(notebook):
    """Display a single notebook as a card"""
    priority = notebook.get('priority', 'Low').lower()
    
    tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in notebook.get('tags', [])])
    
    st.markdown(f"""
    <div class='notebook-card priority-{priority}'>
        <h3>📓 {notebook.get('project_name', 'Unnamed Project')}</h3>
        <p><strong>📁 Category:</strong> {notebook.get('category', 'N/A')}</p>
        <p><strong>📊 Status:</strong> {notebook.get('status', 'N/A')}</p>
        <p><strong>⭐ Priority:</strong> {notebook.get('priority', 'N/A')}</p>
        <p><strong>📝 Description:</strong> {notebook.get('description', 'No description')}</p>
        <p><strong>🏷️ Tags:</strong> {tags_html}</p>
        <p><small>🕒 Created: {notebook.get('created_date', 'N/A')}</small></p>
        <p><small>🔄 Updated: {notebook.get('last_updated', 'N/A')}</small></p>
    </div>
    """, unsafe_allow_html=True)

# Main App
def main():
    st.markdown("<h1 class='main-header'>📓 My Colab Notebook Manager</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.gstatic.com/colaboratory/assets/colab-logo.svg", width=150)
        st.title("📂 Navigation")
        
        # File Upload
        st.markdown("### 📤 Upload Data")
        uploaded_file = st.file_uploader(
            "Upload master_index.json",
            type=['json'],
            help="Upload the master_index.json file from your Google Drive ColabTracker folder"
        )
        
        if uploaded_file:
            data = load_data(uploaded_file)
            if data:
                st.session_state['data'] = data
                st.success(f"✅ Loaded {len(data.get('notebooks', []))} notebooks!")
        
        st.markdown("---")
        
        # Navigation
        if 'data' in st.session_state:
            page = st.radio(
                "Go to:",
                ["🏠 Dashboard", "📚 All Notebooks", "🔍 Search", "📊 Analytics", "📝 Summaries"],
                label_visibility="collapsed"
            )
        else:
            page = "🏠 Dashboard"
        
        st.markdown("---")
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. Open your Google Drive
            2. Go to `ColabTracker` folder
            3. Download `master_index.json`
            4. Upload it above ☝️
            5. Explore your notebooks!
            """)
    
    # Main Content Area
    if 'data' not in st.session_state:
        # Welcome Screen
        st.info("👈 Please upload your master_index.json file from the sidebar to get started!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🚀 Getting Started
            
            1. **Run the tracker** in your Colab notebooks
            2. **Fill in the metadata** form
            3. **Download** the master_index.json file
            4. **Upload** it here to see your dashboard
            
            ### ✨ Features
            
            - 📊 Visual analytics
            - 🔍 Search & filter
            - 📝 Progress tracking
            - 🏷️ Tag management
            """)
        
        with col2:
            st.markdown("""
            ### 📍 Where is master_index.json?
            
            **Google Drive Path:**
            ```
            MyDrive/ColabTracker/master_index.json
            ```
            
            **Steps to download:**
            1. Open Google Drive
            2. Navigate to ColabTracker folder
            3. Right-click master_index.json
            4. Click Download
            5. Upload here!
            """)
        
        return
    
    # Get notebooks data
    notebooks = st.session_state['data'].get('notebooks', [])
    
    # Route to different pages
    if page == "🏠 Dashboard":
        show_dashboard(notebooks)
    elif page == "📚 All Notebooks":
        show_all_notebooks(notebooks)
    elif page == "🔍 Search":
        show_search(notebooks)
    elif page == "📊 Analytics":
        show_analytics(notebooks)
    elif page == "📝 Summaries":
        show_summaries()

def show_dashboard(notebooks):
    """Main dashboard view"""
    st.header("📊 Dashboard Overview")
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(notebooks)
    in_progress = len([n for n in notebooks if n.get('status') == 'In Progress'])
    completed = len([n for n in notebooks if n.get('status') == 'Completed'])
    high_priority = len([n for n in notebooks if n.get('priority') == 'High'])
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>{total}</h2>
            <p>Total Notebooks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>{in_progress}</h2>
            <p>In Progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>{completed}</h2>
            <p>Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>{high_priority}</h2>
            <p>High Priority</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Notebooks and High Priority
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕒 Recent Notebooks")
        recent = sorted(notebooks, key=lambda x: x.get('last_updated', ''), reverse=True)[:5]
        
        for nb in recent:
            display_notebook_card(nb)
    
    with col2:
        st.subheader("⭐ High Priority")
        high_pri = [n for n in notebooks if n.get('priority') == 'High'][:5]
        
        if high_pri:
            for nb in high_pri:
                display_notebook_card(nb)
        else:
            st.info("No high priority notebooks")
    
    # Category Chart
    st.markdown("---")
    st.subheader("📁 Notebooks by Category")
    
    if notebooks:
        categories = {}
        for nb in notebooks:
            cat = nb.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        fig = px.pie(
            values=list(categories.values()),
            names=list(categories.keys()),
            title="Distribution by Category",
            color_discrete_sequence=px.colors.sequential.Purples
        )
        st.plotly_chart(fig, use_container_width=True)

def show_all_notebooks(notebooks):
    """Show all notebooks with filters"""
    st.header("📚 All Notebooks")
    
    if not notebooks:
        st.warning("No notebooks found")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(notebooks)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_cat = st.selectbox("📁 Category", categories)
    
    with col2:
        statuses = ['All'] + sorted(df['status'].unique().tolist())
        selected_status = st.selectbox("📊 Status", statuses)
    
    with col3:
        priorities = ['All'] + sorted(df['priority'].unique().tolist())
        selected_priority = st.selectbox("⭐ Priority", priorities)
    
    # Filter data
    filtered = df.copy()
    
    if selected_cat != 'All':
        filtered = filtered[filtered['category'] == selected_cat]
    
    if selected_status != 'All':
        filtered = filtered[filtered['status'] == selected_status]
    
    if selected_priority != 'All':
        filtered = filtered[filtered['priority'] == selected_priority]
    
    st.info(f"Showing {len(filtered)} of {len(df)} notebooks")
    
    # Display notebooks
    for _, nb in filtered.iterrows():
        display_notebook_card(nb.to_dict())

def show_search(notebooks):
    """Search functionality"""
    st.header("🔍 Search Notebooks")
    
    search_term = st.text_input(
        "Search by name, description, or tags",
        placeholder="Enter search term..."
    )
    
    if search_term:
        results = []
        search_lower = search_term.lower()
        
        for nb in notebooks:
            # Search in multiple fields
            if (search_lower in nb.get('project_name', '').lower() or
                search_lower in nb.get('description', '').lower() or
                any(search_lower in tag.lower() for tag in nb.get('tags', []))):
                results.append(nb)
        
        st.success(f"Found {len(results)} results for '{search_term}'")
        
        for nb in results:
            display_notebook_card(nb)
    else:
        st.info("👆 Enter a search term to find notebooks")

def show_analytics(notebooks):
    """Analytics and visualizations"""
    st.header("📊 Analytics & Insights")
    
    if not notebooks:
        st.warning("No data available")
        return
    
    df = pd.DataFrame(notebooks)
    
    # Timeline
    st.subheader("📈 Notebooks Created Over Time")
    df['created_date'] = pd.to_datetime(df['created_date'])
    df['month'] = df['created_date'].dt.to_period('M').astype(str)
    
    timeline = df.groupby('month').size().reset_index(name='count')
    
    fig = px.bar(
        timeline,
        x='month',
        y='count',
        title="Notebooks Created Per Month",
        color='count',
        color_continuous_scale='Purples'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Status and Priority Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 By Status")
        status_counts = df['status'].value_counts()
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            labels={'x': 'Status', 'y': 'Count'},
            color=status_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⭐ By Priority")
        priority_counts = df['priority'].value_counts()
        fig = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            labels={'x': 'Priority', 'y': 'Count'},
            color=priority_counts.values,
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Popular Tags
    st.subheader("🏷️ Most Used Tags")
    all_tags = []
    for nb in notebooks:
        all_tags.extend(nb.get('tags', []))
    
    if all_tags:
        tag_counts = pd.Series(all_tags).value_counts().head(15)
        fig = px.bar(
            x=tag_counts.values,
            y=tag_counts.index,
            orientation='h',
            labels={'x': 'Count', 'y': 'Tag'},
            title="Top 15 Tags",
            color=tag_counts.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_summaries():
    """Show daily summaries"""
    st.header("📝 Daily Summaries")
    
    uploaded_summary = st.file_uploader(
        "Upload daily_summaries.json",
        type=['json'],
        key='summary_upload'
    )
    
    if uploaded_summary:
        summaries = json.load(uploaded_summary)
        all_summaries = summaries.get('summaries', [])
        
        st.info(f"📊 Total work sessions logged: {len(all_summaries)}")
        
        # Calculate total hours
        total_hours = sum(s.get('hours_worked', 0) for s in all_summaries)
        st.metric("⏱️ Total Hours Logged", f"{total_hours:.1f} hours")
        
        st.markdown("---")
        
        # Display summaries
        for summary in reversed(all_summaries):
            with st.expander(f"📅 {summary.get('date', 'N/A')} - {summary.get('time', '')}"):
                st.markdown(f"**✅ Accomplishments:**")
                st.write(summary.get('accomplishments', 'N/A'))
                
                st.markdown(f"**⚠️ Challenges:**")
                st.write(summary.get('challenges', 'N/A'))
                
                st.markdown(f"**📋 Next Steps:**")
                st.write(summary.get('next_steps', 'N/A'))
                
                st.markdown(f"**⏱️ Time Spent:** {summary.get('hours_worked', 0)} hours")
    else:
        st.info("Upload your daily_summaries.json file to view your work logs")

if __name__ == "__main__":
    main()
