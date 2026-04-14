"""
AI Agent using NEW Google GenAI Package
Automatically analyzes code and generates insights
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the absolute path to the directory where agent.py is
env_path = Path(__file__).resolve().parent / ".env"

# Force load from that specific path
load_dotenv(dotenv_path=env_path, override=True)

print(f"DEBUG: Looking for .env at: {env_path}")
print(f"DEBUG: Key found: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")

import os
from dotenv import load_dotenv
import sqlite3
import json
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Import the NEW Google GenAI package
from google import genai
from google.genai import types

class NotebookAnalyzer:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY not found!\n"
                "Please add it to your .env file:\n"
                "GEMINI_API_KEY=your_key_here"
            )
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Configure the new GenAI client
        self.client = genai.Client(api_key=api_key)
        
    def analyze_notebook(self, code_cells, markdown_cells, notebook_name):
        """Analyze notebook using Gemini AI"""
        
        # Combine code and markdown (limit to avoid token limits)
        all_code = "\n\n".join(code_cells[:10])[:8000]  # Max 8000 chars
        all_markdown = "\n\n".join(markdown_cells[:5])[:2000]  # Max 2000 chars
        
        prompt = f"""
Analyze this Google Colab notebook and provide a structured analysis.

**Notebook Name:** {notebook_name}

**Markdown Documentation:**
{all_markdown if all_markdown else "No documentation provided"}

**Code Content:**
{all_code if all_code else "No code available"}

Please provide a JSON response with the following structure:
{{
    "summary": "A brief 2-3 sentence summary of what this notebook does",
    "main_goal": "The primary objective or problem being solved",
    "category": "Choose ONE: Machine Learning, Deep Learning, Data Analysis, NLP, Computer Vision, Data Science, Research, Tutorial, Experiment, Web Scraping, Automation, Other",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "technologies": ["python", "tensorflow", "pandas", "etc"],
    "key_findings": "Main results or conclusions (if any)",
    "difficulty_level": "Beginner, Intermediate, or Advanced",
    "estimated_time": "Estimated time to run (e.g., '30 minutes', '2 hours')",
    "dataset_used": "Name of dataset if mentioned, or 'Not specified'",
    "model_type": "Type of model if any (e.g., 'CNN', 'LSTM', 'Random Forest', or 'N/A')"
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            # Use the new API
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=1000,
                )
            )
            
            # Extract text from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            print(f"   ✅ AI Analysis complete!")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON parsing error: {e}")
            print(f"   Response was: {response_text[:200]}")
            return self.get_fallback_analysis(code_cells, notebook_name)
        except Exception as e:
            print(f"   ❌ Error analyzing notebook: {e}")
            return self.get_fallback_analysis(code_cells, notebook_name)
    
    def get_fallback_analysis(self, code_cells, notebook_name):
        """Fallback analysis using keyword detection"""
        all_code = "\n".join(code_cells).lower()
        
        # Detect technologies
        tags = []
        technologies = []
        category = "Other"
        
        # Deep Learning
        if 'tensorflow' in all_code or 'keras' in all_code:
            tags.extend(['tensorflow', 'deep-learning', 'neural-networks'])
            technologies.extend(['tensorflow', 'keras'])
            category = "Deep Learning"
        
        if 'pytorch' in all_code or 'torch' in all_code:
            tags.extend(['pytorch', 'deep-learning', 'neural-networks'])
            technologies.append('pytorch')
            category = "Deep Learning"
        
        # Machine Learning
        if 'sklearn' in all_code or 'scikit' in all_code:
            tags.extend(['scikit-learn', 'machine-learning'])
            technologies.append('scikit-learn')
            if category == "Other":
                category = "Machine Learning"
        
        # NLP
        if any(word in all_code for word in ['transformers', 'bert', 'gpt', 'nlp', 'nltk', 'spacy']):
            tags.extend(['nlp', 'text-processing'])
            category = "NLP"
        
        # Computer Vision
        if any(word in all_code for word in ['cv2', 'opencv', 'pil', 'image', 'yolo']):
            tags.extend(['computer-vision', 'image-processing'])
            category = "Computer Vision"
        
        # Data Analysis
        if 'pandas' in all_code:
            tags.append('pandas')
            technologies.append('pandas')
            if category == "Other":
                category = "Data Analysis"
        
        if 'numpy' in all_code:
            tags.append('numpy')
            technologies.append('numpy')
        
        if 'matplotlib' in all_code or 'seaborn' in all_code or 'plotly' in all_code:
            tags.append('visualization')
            technologies.append('matplotlib')
        
        # Web Scraping
        if any(word in all_code for word in ['beautifulsoup', 'selenium', 'scrapy', 'requests']):
            tags.extend(['web-scraping', 'automation'])
            category = "Web Scraping"
        
        # Remove duplicates
        tags = list(set(tags))
        technologies = list(set(technologies))
        
        if not tags:
            tags = ['untagged']
        
        if not technologies:
            technologies = ['python']
        
        return {
            "summary": f"Notebook: {notebook_name}",
            "main_goal": "Automated analysis - manual review recommended",
            "category": category,
            "tags": tags[:8],  # Limit to 8 tags
            "technologies": technologies,
            "key_findings": "Not analyzed by AI",
            "difficulty_level": "Unknown",
            "estimated_time": "Unknown",
            "dataset_used": "Not specified",
            "model_type": "N/A"
        }
    
    def analyze_all_unanalyzed(self, db_path='database.db'):
        """Analyze all notebooks that haven't been analyzed yet"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get unanalyzed notebooks
        cursor.execute('''
            SELECT id, name, code_content, markdown_content 
            FROM notebooks 
            WHERE analyzed = 0 OR analyzed IS NULL
        ''')
        
        notebooks = cursor.fetchall()
        
        if not notebooks:
            print("✅ All notebooks are already analyzed!")
            conn.close()
            return
        
        print(f"\n🤖 Found {len(notebooks)} notebooks to analyze\n")
        
        successful = 0
        failed = 0
        
        for i, (nb_id, name, code_content, markdown_content) in enumerate(notebooks, 1):
            print(f"[{i}/{len(notebooks)}] Analyzing: {name}")
            
            code_cells = json.loads(code_content) if code_content else []
            markdown_cells = json.loads(markdown_content) if markdown_content else []
            
            # Skip empty notebooks
            if not code_cells:
                print("   ⚠️ Skipping - no code found")
                continue
            
            try:
                # Analyze with AI
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
                
                print(f"   📁 Category: {analysis.get('category')}")
                print(f"   🏷️ Tags: {', '.join(analysis.get('tags', [])[:5])}")
                successful += 1
                
                # Rate limiting - wait between requests
                if i < len(notebooks):
                    time.sleep(2)  # Wait 2 seconds between API calls
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
                continue
        
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"📊 Analysis Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total: {len(notebooks)}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    print("🧠 Starting AI Analysis...\n")
    
    try:
        analyzer = NotebookAnalyzer()
        analyzer.analyze_all_unanalyzed()
        print("\n✅ Analysis complete! Run: streamlit run app.py")
    except ValueError as e:
        print(f"\n{e}")
        print("\nTo fix this:")
        print("1. Get your API key from: https://aistudio.google.com/app/apikey")
        print("2. Add it to .env file:")
        print("   GEMINI_API_KEY=your_api_key_here")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")