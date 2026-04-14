"""
Multi-Account Google Drive Scanner
Properly handles multiple Google accounts
"""

import os
import pickle
import json
from datetime import datetime
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class DriveScanner:
    def __init__(self, account_name="Account1", credentials_file='credentials.json'):
        self.account_name = account_name
        self.creds = None
        self.service = None
        self.token_file = f'token_{account_name}.pickle'
        self.credentials_file = credentials_file
        
    def authenticate(self):
        """Authenticate with Google Drive for specific account"""
        print(f"\n{'='*60}")
        print(f"🔐 Authenticating {self.account_name}")
        print(f"{'='*60}\n")
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            print(f"📁 Found existing token: {self.token_file}")
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
            
            # Check which account is logged in
            if self.creds and self.creds.valid:
                try:
                    service = build('drive', 'v3', credentials=self.creds)
                    about = service.about().get(fields="user").execute()
                    email = about['user']['emailAddress']
                    print(f"✅ Already logged in as: {email}")
                    self.service = service
                    return True
                except:
                    print("⚠️ Token expired, need to re-authenticate")
                    self.creds = None
        
        # Refresh or create new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Refreshing token...")
                self.creds.refresh(Request())
            else:
                print(f"\n⚠️ IMPORTANT: Login with the CORRECT account for {self.account_name}")
                print("=" * 60)
                
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Error: {self.credentials_file} not found!")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, 
                    SCOPES,
                    redirect_uri='http://localhost:8080/'
                )
                
                # Run local server for OAuth
                self.creds = flow.run_local_server(
                    port=8080,
                    prompt='consent',  # Force account selection
                    success_message='✅ Authentication successful! You can close this window.'
                )
            
            # Save the credentials for next time
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            print(f"💾 Saved credentials to: {self.token_file}")
        
        self.service = build('drive', 'v3', credentials=self.creds)
        
        # Verify which account we're logged into
        try:
            about = self.service.about().get(fields="user").execute()
            email = about['user']['emailAddress']
            print(f"✅ Successfully authenticated as: {email}")
            
            # Save the email for reference
            with open(f'{self.account_name}_email.txt', 'w') as f:
                f.write(email)
            
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def get_all_colab_notebooks(self):
        """Get all Colab notebooks from Drive"""
        notebooks = []
        page_token = None
        
        print("🔍 Searching for notebooks...")
        
        while True:
            try:
                response = self.service.files().list(
                    q="(mimeType='application/x-ipynb+json' or name contains '.ipynb') and trashed=false",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, modifiedTime, createdTime, webViewLink, parents, size)',
                    pageToken=page_token,
                    pageSize=100
                ).execute()
                
                files = response.get('files', [])
                notebooks.extend(files)
                
                if files:
                    print(f"   Found {len(files)} notebooks in this batch...")
                
                page_token = response.get('nextPageToken', None)
                
                if page_token is None:
                    break
                    
            except Exception as e:
                print(f"❌ Error fetching notebooks: {e}")
                break
        
        print(f"✅ Total notebooks found: {len(notebooks)}")
        return notebooks
    
    def download_notebook_content(self, file_id, file_name):
        """Download notebook content"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            content = fh.read().decode('utf-8', errors='ignore')
            return json.loads(content)
            
        except json.JSONDecodeError:
            print(f"   ⚠️ Warning: {file_name} is not valid JSON")
            return None
        except Exception as e:
            print(f"   ❌ Error downloading {file_name}: {str(e)[:100]}")
            return None
    
    def extract_code_from_notebook(self, notebook_content):
        """Extract all code cells"""
        if not notebook_content or 'cells' not in notebook_content:
            return []
        
        code_cells = []
        for cell in notebook_content.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                if isinstance(source, list):
                    code = ''.join(source)
                else:
                    code = source
                if code.strip():
                    code_cells.append(code)
        
        return code_cells
    
    def extract_markdown_from_notebook(self, notebook_content):
        """Extract all markdown cells"""
        if not notebook_content or 'cells' not in notebook_content:
            return []
        
        markdown_cells = []
        for cell in notebook_content.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                source = cell.get('source', [])
                if isinstance(source, list):
                    text = ''.join(source)
                else:
                    text = source
                if text.strip():
                    markdown_cells.append(text)
        
        return markdown_cells
    
    def scan_and_store(self, db_path='database.db'):
        """Scan all notebooks and store in database"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting scan for {self.account_name}")
        print(f"{'='*60}\n")
        
        if not self.authenticate():
            print("❌ Authentication failed!")
            return []
        
        notebooks = self.get_all_colab_notebooks()
        
        if not notebooks:
            print("⚠️ No notebooks found in this account.")
            return []
        
        results = []
        successful = 0
        failed = 0
        
        for i, nb in enumerate(notebooks, 1):
            print(f"\n[{i}/{len(notebooks)}] Processing: {nb['name'][:50]}")
            
            content = self.download_notebook_content(nb['id'], nb['name'])
            
            if content:
                code_cells = self.extract_code_from_notebook(content)
                markdown_cells = self.extract_markdown_from_notebook(content)
                
                notebook_data = {
                    'id': nb['id'],
                    'name': nb['name'],
                    'account': self.account_name,  # Use account name
                    'created_time': nb.get('createdTime'),
                    'modified_time': nb.get('modifiedTime'),
                    'web_link': nb.get('webViewLink', ''),
                    'colab_link': f"https://colab.research.google.com/drive/{nb['id']}",
                    'size': nb.get('size', 0),
                    'code_cells': code_cells,
                    'markdown_cells': markdown_cells,
                    'total_code_lines': sum(len(code.split('\n')) for code in code_cells),
                    'scanned_at': datetime.now().isoformat()
                }
                
                results.append(notebook_data)
                self.save_to_database(notebook_data, db_path)
                
                print(f"   ✅ Success! ({len(code_cells)} cells, {notebook_data['total_code_lines']} lines)")
                successful += 1
            else:
                print(f"   ❌ Failed")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Summary for {self.account_name}:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total: {len(notebooks)}")
        print(f"{'='*60}\n")
        
        return results
    
    def save_to_database(self, notebook_data, db_path):
        """Save to database"""
        conn = sqlite3.connect(db_path)
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
        
        cursor.execute('''
            INSERT OR REPLACE INTO notebooks 
            (id, name, account, created_time, modified_time, web_link, colab_link, 
             size, code_content, markdown_content, total_code_lines, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notebook_data['id'],
            notebook_data['name'],
            notebook_data['account'],
            notebook_data['created_time'],
            notebook_data['modified_time'],
            notebook_data['web_link'],
            notebook_data['colab_link'],
            notebook_data['size'],
            json.dumps(notebook_data['code_cells']),
            json.dumps(notebook_data['markdown_cells']),
            notebook_data['total_code_lines'],
            notebook_data['scanned_at']
        ))
        
        conn.commit()
        conn.close()

def scan_all_accounts():
    """Scan multiple accounts sequentially"""
    print("\n🤖 Multi-Account Colab Scanner")
    print("=" * 60)
    
    # Define your accounts here
    accounts = [
        {"name": "Account1", "description": "Primary Gmail"},
        {"name": "Account2", "description": "Secondary Gmail"},
    ]
    
    for account in accounts:
        print(f"\n\n📧 Ready to scan: {account['description']}")
        input("Press ENTER when ready (make sure you'll login to the CORRECT account)...")
        
        scanner = DriveScanner(account['name'])
        try:
            scanner.scan_and_store()
        except Exception as e:
            print(f"❌ Error scanning {account['name']}: {e}")
            continue
    
    print("\n\n✅ All accounts scanned!")
    print("Next step: python agent.py")

def scan_single_account(account_name):
    """Scan a single account"""
    scanner = DriveScanner(account_name)
    scanner.scan_and_store()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Scan specific account: python scanner.py Account1
        account_name = sys.argv[1]
        print(f"Scanning single account: {account_name}")
        scan_single_account(account_name)
    else:
        # Scan all accounts
        scan_all_accounts()