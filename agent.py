"""
AI Agent using Google Gemini
Properly analyzes notebooks and generates meaningful summaries
"""

import os
import json
import sqlite3
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

# Import the correct Gemini package
try:
    import google.generativeai as genai
except ImportError:
    print("Installing google-generativeai...")
    os.system("pip install google-generativeai")
    import google.generativeai as genai


class NotebookAnalyzer:
    """Analyzes Colab notebooks using Google Gemini AI"""
    
    def __init__(self):
        # Get API key
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("""
            ❌ GEMINI_API_KEY not found!
            
            To fix:
            1. Get API key from: https://aistudio.google.com/app/apikey
            2. Create .env file in project folder
            3. Add: GEMINI_API_KEY=your_actual_key_here
            """)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ Gemini AI initialized successfully")
    
    def analyze_notebook(self, code_cells, markdown_cells, notebook_name):
        """Analyze a single notebook and generate insights"""
        
        # Combine code (limit to avoid token limits)
        all_code = "\n\n".join(code_cells[:10])  # First 10 code cells
        all_markdown = "\n\n".join(markdown_cells[:5])  # First 5 markdown cells
        
        # Skip if no code
        if not all_code.strip():
            return self.get_empty_analysis(notebook_name)
        
        # Create detailed prompt
        prompt = f"""You are an expert at analyzing Jupyter/Colab notebooks. Analyze this notebook and provide detailed insights.

NOTEBOOK NAME: {notebook_name}

MARKDOWN/DOCUMENTATION:
{all_markdown if all_markdown else "No markdown documentation"}

CODE CONTENT:
{all_code[:4000]}

Please analyze this notebook and respond with ONLY a valid JSON object (no markdown, no code blocks, just pure JSON) with this exact structure:

{{
    "summary": "A clear, detailed 2-3 sentence description of what this notebook does and accomplishes. Be specific about the techniques, datasets, or problems addressed.",
    "main_goal": "The primary objective this notebook is trying to achieve. What problem is it solving?",
    "category": "Choose the MOST relevant ONE: Machine Learning, Deep Learning, Data Analysis, NLP, Computer Vision, Data Science, Web Scraping, Automation, Tutorial, Research, Experiment, Other",
    "tags": ["list", "5-8", "relevant", "technology", "keywords"],
    "technologies": ["python", "specific libraries used"],
    "key_findings": "Main results, conclusions, or insights from this notebook (if any)",
    "difficulty_level": "Beginner, Intermediate, or Advanced",
    "dataset_used": "Name of dataset if mentioned, otherwise 'Not specified'",
    "model_type": "Type of ML/DL model if any (e.g., 'Random Forest', 'CNN', 'LSTM') or 'N/A'"
}}

IMPORTANT: 
- Respond ONLY with the JSON object
- NO markdown code blocks (```json)
- NO additional text before or after
- Make the summary informative and specific
- Infer details from the code if documentation is sparse"""

        try:
            # Generate content
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            response_text = self.clean_json_response(response_text)
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Validate and fix summary
            if analysis.get('summary', '').startswith('Notebook:'):
                analysis['summary'] = self.generate_fallback_summary(code_cells, notebook_name)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            print(f"Response was: {response_text[:200]}...")
            return self.get_fallback_analysis(code_cells, markdown_cells, notebook_name)
        
        except Exception as e:
            print(f"❌ Error analyzing: {e}")
            return self.get_fallback_analysis(code_cells, markdown_cells, notebook_name)
    
    def clean_json_response(self, text):
        """Clean JSON response from potential markdown formatting"""
        # Remove markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def generate_fallback_summary(self, code_cells, notebook_name):
        """Generate a basic summary from code analysis"""
        all_code = "\n".join(code_cells).lower()
        
        summary_parts = []
        
        # Detect data science operations
        if any(word in all_code for word in ['pd.read_csv', 'load_dataset', 'dataframe']):
            summary_parts.append("performs data loading and processing")
        
        if any(word in all_code for word in ['model.fit', 'train', 'classifier']):
            summary_parts.append("includes machine learning model training")
        
        if any(word in all_code for word in ['plt.', 'seaborn', 'plotly', 'visualization']):
            summary_parts.append("creates data visualizations")
        
        if any(word in all_code for word in ['scrape', 'requests.get', 'beautifulsoup']):
            summary_parts.append("performs web scraping")
        
        if any(word in all_code for word in ['tensorflow', 'keras', 'torch', 'neural']):
            summary_parts.append("implements deep learning models")
        
        if summary_parts:
            return f"This notebook {', '.join(summary_parts)}."
        else:
            return f"A Colab notebook focusing on {self.detect_main_library(all_code)} with {len(code_cells)} code cells."
    
    def detect_main_library(self, code):
        """Detect the main library being used"""
        libraries = {
            'pandas': 'data manipulation',
            'numpy': 'numerical computing',
            'sklearn': 'machine learning',
            'tensorflow': 'deep learning',
            'pytorch': 'deep learning',
            'matplotlib': 'visualization',
            'seaborn': 'statistical visualization',
            'requests': 'API/web requests',
            'beautifulsoup': 'web scraping',
        }
        
        for lib, desc in libraries.items():
            if lib in code:
                return desc
        
        return 'Python programming'
    
    def get_fallback_analysis(self, code_cells, markdown_cells, notebook_name):
        """Fallback analysis when AI fails"""
        all_code = "\n".join(code_cells).lower()
        
        # Detect technologies
        tags = []
        
        if 'pandas' in all_code:
            tags.append('pandas')
        if 'numpy' in all_code:
            tags.append('numpy')
        if 'matplotlib' in all_code or 'seaborn' in all_code:
            tags.extend(['visualization', 'plotting'])
        if 'sklearn' in all_code:
            tags.extend(['scikit-learn', 'machine-learning'])
        if 'tensorflow' in all_code or 'keras' in all_code:
            tags.extend(['tensorflow', 'deep-learning'])
        if 'torch' in all_code:
            tags.extend(['pytorch', 'deep-learning'])
        if 'requests' in all_code or 'beautifulsoup' in all_code:
            tags.extend(['web-scraping', 'automation'])
        
        # Detect category
        category = "Data Analysis"
        if any(word in all_code for word in ['model.fit', 'classifier', 'regressor']):
            category = "Machine Learning"
        if any(word in all_code for word in ['keras', 'tensorflow', 'torch', 'neural']):
            category = "Deep Learning"
        if any(word in all_code for word in ['scrape', 'requests.get']):
            category = "Web Scraping"
        
        return {
            "summary": self.generate_fallback_summary(code_cells, notebook_name),
            "main_goal": "Code analysis and data processing",
            "category": category,
            "tags": tags if tags else ["python", "data-analysis"],
            "technologies": tags,
            "key_findings": "Automated analysis - manual review recommended",
            "difficulty_level": "Intermediate",
            "dataset_used": "Not specified",
            "model_type": "N/A"
        }
    
    def get_empty_analysis(self, notebook_name):
        """Analysis for empty notebooks"""
        return {
            "summary": f"Empty or new notebook named {notebook_name}",
            "main_goal": "Not yet developed",
            "category": "Other",
            "tags": ["empty", "new"],
            "technologies": [],
            "key_findings": "No code to analyze",
            "difficulty_level": "Beginner",
            "dataset_used": "None",
            "model_type": "N/A"
        }
    
    def analyze_all_unanalyzed(self, db_path='database.db'):
        """Analyze all notebooks that haven't been analyzed yet"""
        
        if not os.path.exists(db_path):
            print("❌ Database not found. Run scanner.py first!")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get unanalyzed notebooks
        cursor.execute('''
            SELECT id, name, code_content, markdown_content 
            FROM notebooks 
            WHERE analyzed = 0 OR analyzed IS NULL
        ''')
        
        notebooks = cursor.fetchall()
        total = len(notebooks)
        
        if total == 0:
            print("✅ All notebooks already analyzed!")
            conn.close()
            return
        
        print(f"\n{'='*60}")
        print(f"🤖 Starting AI Analysis")
        print(f"{'='*60}")
        print(f"Found {total} notebooks to analyze\n")
        
        analyzed_count = 0
        failed_count = 0
        
        for i, (nb_id, name, code_content, markdown_content) in enumerate(notebooks, 1):
            print(f"\n[{i}/{total}] 📓 {name}")
            print(f"{'─'*60}")
            
            # Parse content
            try:
                code_cells = json.loads(code_content) if code_content else []
                markdown_cells = json.loads(markdown_content) if markdown_content else []
            except:
                code_cells = []
                markdown_cells = []
            
            # Skip empty notebooks
            if not code_cells:
                print("⚠️  Skipping - No code found")
                continue
            
            # Analyze
            try:
                analysis = self.analyze_notebook(code_cells, markdown_cells, name)
                
                # Update database
                cursor.execute('''
                    UPDATE notebooks
                    SET analyzed = 1,
                        summary = ?,
                        tags = ?,
                        category = ?,
                        main_goal = ?,
                        key_findings = ?,
                        technologies = ?
                    WHERE id = ?
                ''', (
                    analysis.get('summary'),
                    json.dumps(analysis.get('tags', [])),
                    analysis.get('category'),
                    analysis.get('main_goal'),
                    analysis.get('key_findings'),
                    json.dumps(analysis.get('technologies', [])),
                    nb_id
                ))
                
                conn.commit()
                
                print(f"✅ Analyzed successfully!")
                print(f"   Category: {analysis.get('category')}")
                print(f"   Summary: {analysis.get('summary')[:80]}...")
                print(f"   Tags: {', '.join(analysis.get('tags', [])[:5])}")
                
                analyzed_count += 1
                
                # Rate limiting - wait between requests
                if i < total:
                    time.sleep(3)  # Wait 3 seconds between API calls
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                failed_count += 1
                continue
        
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"🎉 Analysis Complete!")
        print(f"{'='*60}")
        print(f"✅ Successfully analyzed: {analyzed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📊 Total processed: {total}")
        print(f"\nRun 'streamlit run app.py' to view your organized notebooks!")


def main():
    """Main execution"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        🤖 AI Notebook Analyzer with Gemini              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        analyzer = NotebookAnalyzer()
        analyzer.analyze_all_unanalyzed()
        
    except ValueError as e:
        print(str(e))
        print("\n💡 Get your free API key here:")
        print("   https://aistudio.google.com/app/apikey")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file has GEMINI_API_KEY")
        print("   2. Verify database.db exists (run scanner.py first)")
        print("   3. Check internet connection")


if __name__ == "__main__":
    main()
