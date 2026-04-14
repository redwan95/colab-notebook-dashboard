import os
import json
import sqlite3
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    os.system("pip install google-generativeai")
    import google.generativeai as genai

class NotebookAnalyzer:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI initialized")

    def analyze_notebook(self, code_cells, markdown_cells, notebook_name):
        # Join the code snippets and markdown into usable text
        all_code = "\n---\n".join(code_cells[:15]) 
        all_text = "\n".join(markdown_cells[:10])
        
        prompt = f"""
        Analyze the Google Colab notebook: '{notebook_name}'
        
        CONTENT TO ANALYZE:
        {all_code}
        {all_text}

        TASK:
        Provide a professional AI analysis of this script.
        
        Return ONLY a JSON object with these exact keys:
        {{
            "category": "One word (e.g., Automation, AI, WebScraping, Data)",
            "summary": "A 2-sentence summary. Use <strong></strong> for key libraries/actions.",
            "tags": ["list", "of", "5", "libraries"],
            "main_goal": "The specific technical outcome of this script"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Robust JSON cleaning
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
            
            return json.loads(raw_text.strip())
        except Exception as e:
            print(f"   ⚠️ AI Parsing Error: {e}")
            return None

    def analyze_all_unanalyzed(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # We only want ones that are NOT analyzed OR have no summary
        cursor.execute("SELECT id, name, code_content FROM notebooks WHERE analyzed = 0 OR summary IS NULL")
        rows = cursor.fetchall()
        
        if not rows:
            print("✨ No notebooks need analysis.")
            return

        for row in rows:
            nb_id, name, content = row
            print(f"🤖 Analyzing: {name}...")
            
            try:
                # 1. Handle JSON or Raw Text
                try:
                    nb_data = json.loads(content)
                    cells = nb_data.get('cells', [])
                    code_snippets = ["".join(c.get('source', [])) for c in cells if c.get('cell_type') == 'code']
                    full_text = "\n".join(code_snippets[:15]) # Get first 15 cells
                except:
                    full_text = str(content)[:5000] # Fallback to raw text

                # 2. Get AI Analysis
                analysis = self.analyze_notebook([full_text], [], name)
                
                if analysis:
                    # 3. Force update the database
                    cursor.execute("""
                        UPDATE notebooks 
                        SET category = ?, summary = ?, tags = ?, main_goal = ?, analyzed = 1 
                        WHERE id = ?
                    """, (
                        analysis.get('category', 'Other'),
                        analysis.get('summary', 'No summary generated'),
                        json.dumps(analysis.get('tags', [])),
                        analysis.get('main_goal', 'No goal specified'),
                        nb_id
                    ))
                    conn.commit()
                    print(f"   ✅ Saved summary for {name}")
                
                time.sleep(2) # Avoid hitting API limits
                
            except Exception as e:
                print(f"   ❌ Failed on {name}: {e}")
        
        conn.close()
        print("\n🎉 Analysis finished. Run 'streamlit run app.py' to see results!")

if __name__ == "__main__":
    analyzer = NotebookAnalyzer()
    analyzer.analyze_all_unanalyzed()
