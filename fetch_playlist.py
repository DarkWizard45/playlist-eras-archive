import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path("playlist-github-fetcher") / ".env")

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
BASE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"

# Set up headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Recursive function to explore folders 
def list_contents(path=""):
    url = f"{BASE_API_URL}/{path}" if path else BASE_API_URL
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item['type'] == 'file':
                print(f"File: {item['path']}")
            elif item['type'] == 'dir': 
                print(f"\n📁 Folder: {item['path']}")
                list_contents(item['path'])  # Recursively go into folders
    else:
        print(f"❌ Failed to fetch contents at path: {path}")
        print(response.text)

# === RUN ===
if __name__ == "__main__":
    print(f"\n📦 Listing all files in GitHub repo '{REPO_OWNER}/{REPO_NAME}'...\n")
    list_contents()