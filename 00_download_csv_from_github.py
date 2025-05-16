import requests
import os

# Configuration to set API url (github repository)
GITHUB_USER = 'icra'
GITHUB_REPO = 'recreate-exports'
BRANCH = 'main'
FILENAME_KEYWORD = '0'  #set keywords to search for the desired csv files ('0' will download all csv files at once)
SAVE_DIR = 'D:/recreate-exports' #change accordingly

# API URL
API_URL = f'https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/git/trees/{BRANCH}?recursive=1'

# Request the file tree

print(f"Searching file list from {API_URL} ...")
response = requests.get(API_URL)
response.raise_for_status()

files = response.json().get('tree', [])

# Filter matching CSVs
csv_files = [f['path'] for f in files if f['path'].endswith('.csv') and FILENAME_KEYWORD in f['path']]

print(f"Found {len(csv_files)} matching CSV files.")


# Download each file if not already present
os.makedirs(SAVE_DIR, exist_ok=True)

for path in csv_files:
    filename = os.path.basename(path)
    dest_path = os.path.join(SAVE_DIR, filename)

    if os.path.exists(dest_path):
        print(f"Skipping (already exists): {filename}")
        continue

    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/{path}"
    print(f"Downloading: {path} to {dest_path}")
    
    r = requests.get(raw_url)
    r.raise_for_status()

    with open(dest_path, 'wb') as f:
        f.write(r.content)

print("Done. Files saved to:", SAVE_DIR)


