"""
Standalone script to fetch the latest features from the backend API
and update the local dummy_features.json file.
"""
import sys
from services.api_service import fetch_features_from_api
from utils.file_utils import save_features

# --- IMPORTANT ---
# REPLACE THIS WITH THE ACTUAL URL OF YOUR BACKEND API
BACKEND_API_URL = "http://your-backend-api.com/features"

def update_features():
    """
    Fetches features from the API and saves them to the local JSON file.
    """
    print(f"Fetching features from {BACKEND_API_URL}...")
    try:
        features = fetch_features_from_api(BACKEND_API_URL)
        print(f"Successfully fetched {len(features)} features.")
        
        save_features(features)
        print("Successfully updated 'resources/dummy_features.json'.")
        
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if "your-backend-api.com" in BACKEND_API_URL:
        print("Please open 'update_features.py' and set the `BACKEND_API_URL` variable.", file=sys.stderr)
        sys.exit(1)
        
    update_features() 