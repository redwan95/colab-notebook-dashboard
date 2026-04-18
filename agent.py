"""
AI Notebook Analyzer
Analyzes Google Colab notebooks using Google Gemini AI
Fixed version - works with new google-genai package
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import time
import re

load_dotenv()

# ============================================
# INSTALL AND IMPORT GEMINI
# ============================================
try:
    from google import genai
except ImportError:
    print("Installing google-genai...")
    os.system("pip install google-genai")
    from google import genai

# ============================================
# CONFIGURATION
# ============================================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("   Please create a .env file with: GEMINI_API_KEY=your_key_here")
    GEMINI_API_KEY = input("Enter your Gemini API key: ").strip()

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"


# ============================================
# ANALYSIS FUNCTIONS
# ============================================
def analyze_code(code_cells):
    """Analyze code to determine category and technologies"""
    all_code = "\n".join(code_cells).lower()
    
    technologies = []
    category = "Other"
    
    # Detect technologies
    tech_patterns = {
        'tensorflow': ['tensorflow', 'tf.', 'tf ', 'keras'],
        'pytorch': ['torch', 'pytorch', 'nn.module'],
        'sklearn': ['sklearn', 'scikit', 'from sklearn', 'import sklearn'],
        'pandas': ['pandas', 'pd.read', 'pd.concat', 'pd.merge'],
        'numpy': ['numpy', 'np.', 'import numpy'],
        'matplotlib': ['matplotlib', 'plt.', 'plt ', 'seaborn'],
        'opencv': ['cv2', 'opencv', 'imread', 'imwrite'],
        'nltk': ['nltk', 'word_tokenize', 'stopwords'],
        'transformers': ['transformers', 'bert', 'gpt', 'huggingface'],
        'xgboost': ['xgboost', 'xgb'],
        'keras': ['keras', 'Dense', 'Sequential'],
        'flask': ['flask', '@app.route'],
        'django': ['django'],
        'fastapi': ['fastapi', '@app.get'],
        'streamlit': ['streamlit', 'st.', 'st '],
        'sqlalchemy': ['sqlalchemy', 'sessionmaker'],
        'requests': ['requests', 'requests.get', 'requests.post'],
        'beautifulsoup': ['beautifulsoup', 'bs4', 'soup.find'],
        'selenium': ['selenium', 'webdriver'],
        'plotly': ['plotly', 'px.', 'go.'],
    }
    
    for tech, patterns in tech_patterns.items():
        if any(p in all_code for p in patterns):
            technologies.append(tech)
    
    if not technologies:
        if any(x in all_code for x in ['df', 'dataset', 'csv', 'excel']):
            technologies.append('pandas')
        if any(x in all_code for x in ['array', 'matrix', 'vector']):
            technologies.append('numpy')
    
    # Detect category
    category_patterns = {
        'Machine Learning': ['model', 'train', 'fit', 'predict', 'classifier', 'regressor', 'accuracy', 'score'],
        'Deep Learning': ['tensorflow', 'torch', 'neural', 'layer', 'conv', 'lstm', 'rnn', 'embedding'],
        'Data Analysis': ['pandas', 'df', 'groupby', 'plot', 'visualization', 'statistics'],
        'NLP': ['nlp', 'text', 'tokenize', 'embedding', 'transformer', 'bert', 'nltk', 'spacy'],
        'Computer Vision': ['image', 'cv2', 'opencv', 'pixel', 'resize', 'crop', 'detect'],
        'Web Scraping': ['requests', 'beautifulsoup', 'selenium', 'scrap', 'crawl'],
        'Automation': ['automate', 'script', 'batch', 'schedule', 'cron'],
        'Data Science': ['scipy', 'statistics', 'hypothesis', 'regression', 'correlation'],
        'Research': ['paper', 'experiment', 'study', 'research', 'analysis'],
        'Tutorial': ['learn', 'tutorial', 'example', 'demo', 'guide', 'course'],
    }
    
    for cat, patterns in category_patterns.items():
        if sum(1 for p in patterns if p in all_code) >= 2:
            category = cat
            break
    
    return list(set(technologies)), category


def generate_summary_with_ai(code_cells, name):
    """Generate proper summary using Gemini AI"""
    
    # Prepare code for analysis (limit to avoid token limits)
    code_sample = "\n\n".join(code_cells[:10])
    if len(code_sample) > 3000:
        code_sample = code_sample[:3000] + "\n\n... [truncated]"
    
    # First try Gemini
    prompt = f"""Analyze this Python code from a Google Colab notebook named "{name}".

CODE:
```python
{code_sample}
