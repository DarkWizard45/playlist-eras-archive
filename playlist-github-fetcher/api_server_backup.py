from flask import Flask, jsonify, Response
import os
import requests
import base64
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse 

# Load environment variables
load_dotenv(dotenv_path=Path('.') / '.env')

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# Set up Flask app
app = Flask(__name__)

# === HELPER FUNCTIONS ===

def get_blob_sha(filepath):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filepath}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    print(f"Fetching SHA from: {url}")

    if response.status_code == 200:
        metadata = response.json()
        sha = metadata.get('sha')
        print(f"Found SHA: {sha}")
        return sha
    else:
        print(f"Error getting file SHA: {response.status_code} - {response.text}")
        return None

def fetch_file_via_blob(filepath):
    encoded_path = urllib.parse.quote(filepath)
    sha = get_blob_sha(encoded_path)
    if not sha:
        return None, 404

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs/{sha}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    print(f"Fetching blob from: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        blob = response.json()
        content_encoded = blob.get('content')
        if content_encoded:
            content_bytes = base64.b64decode(content_encoded)
            print("Successfully decoded file.")
            return content_bytes, 200
        else:
            print("No content found in blob.")
            return None, 500
    else:
        print(f"Error fetching blob: {response.status_code} - {response.text}")
        return None, response.status_code

# === ROUTES ===

@app.route("/")
def home():
    return jsonify({"message": "Spotify Data Server (Blob API Mode) is running!"})

@app.route("/file/<path:filepath>")
def get_file(filepath):
    content, status_code = fetch_file_via_blob(filepath)
    if status_code == 200 and content:
        return Response(content, mimetype="application/json")
    else:
        return jsonify({"error": "File not found", "status": status_code}), status_code

# === RUN SERVER ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

