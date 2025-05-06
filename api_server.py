from flask import Flask, jsonify, Response, stream_with_context, send_from_directory
import os
import requests
import base64
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse

# Load environment variables
load_dotenv(dotenv_path=Path("playlist-github-fetcher") / ".env")

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
    print(f"[DEBUG] Fetching SHA for path: {filepath}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get('sha')
        print(f"[DEBUG] Found SHA: {sha}")
        return sha
    else:
        print(f"[ERROR] Could not fetch SHA for {filepath}. Status: {response.status_code}")
        return None

def fetch_file_via_blob(filepath):
    sha = get_blob_sha(filepath)
    if not sha:
        return None, 404

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs/{sha}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    print(f"[DEBUG] Fetching blob content from SHA: {sha}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content_encoded = response.json().get('content')
        if content_encoded:
            content_bytes = base64.b64decode(content_encoded)
            print(f"[DEBUG] Successfully decoded content from blob")
            return content_bytes, 200
        else:
            print("[ERROR] Blob returned no content")
            return None, 500
    else:
        print(f"[ERROR] Failed to fetch blob for SHA {sha}. Status: {response.status_code}")
        return None, response.status_code

# === ROUTES ===

@app.route("/")
def home():
    return jsonify({"message": "Spotify Data Server is running!"})

@app.route("/file/<path:filepath>")
def get_file(filepath):
    print(f"[DEBUG] STREAMING /file/{filepath}")
    content, status_code = fetch_file_via_blob(filepath)
    if status_code == 200 and content:
        def generate():
            yield content
        return Response(stream_with_context(generate()), mimetype="application/json")
    else:
        return jsonify({"error": "File not found", "status": status_code}), status_code
@app.route("/openapi.yaml")
def openapi_yaml():
    print(f"[DEBUG] GET /openapi.yaml")
    content, status_code = fetch_file_via_blob(".well-known/openapi.yaml")
    if status_code == 200 and content:
        return Response(content, mimetype="text/yaml")
    else:
        return jsonify({"error": "OpenAPI spec not found", "status": status_code}), status_code

@app.route("/list-dir/<path:dirpath>")
def list_directory(dirpath):
    full_path = os.path.join(os.getcwd(), dirpath)
    print(f"[DEBUG] Listing contents of: {full_path}")
    if not os.path.exists(full_path):
        return jsonify({"error": "Directory not found", "path": full_path}), 404
    if not os.path.isdir(full_path):
        return jsonify({"error": "Not a directory", "path": full_path}), 400

    files = os.listdir(full_path)
    return jsonify({
        "directory": dirpath,
        "full_path": full_path,
        "files": files
    })

@app.route("/file/data/playlist_filename_map.json")
def serve_playlist_filename_map():
    github_url = "https://darkwizard45.github.io/playlist-eras-archive/static/data/wave_playlist_map.json"
    response = requests.get(github_url)
    return Response(response.content, mimetype="application/json")

# === RUN SERVER ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)