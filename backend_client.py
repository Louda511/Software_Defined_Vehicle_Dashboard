import requests
import json
from typing import List, Dict, Any

class BackendClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_features(self) -> List[Dict[str, Any]]:
        """
        Fetch features from the backend and convert them to the expected format.
        
        Returns:
            List of feature dictionaries with the structure:
            {
                'name': str,
                'icon': str,  # converted from 'image'
                'short_desc': str,  # converted from 'description'
                'location': str
            }
        """
        try:
            # Make API call to backend
            response = requests.get(f"{self.base_url}/api/features")
            response.raise_for_status()
            
            # Parse the response
            backend_features = response.json()
            
            # Convert backend format to frontend format
            converted_features = []
            for feature in backend_features:
                converted_feature = {
                    'name': feature.get('name', ''),
                    'icon': feature.get('image', ''),  # backend 'image' -> frontend 'icon'
                    'short_desc': feature.get('description', ''),  # backend 'description' -> frontend 'short_desc'
                    'location': feature.get('location', '')
                }
                converted_features.append(converted_feature)
            
            return converted_features
            
        except requests.RequestException as e:
            print(f"Error fetching features from backend: {e}")
            # Return empty list or fallback to local data
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing backend response: {e}")
            return []

def get_features_from_backend(base_url: str = "http://localhost:8000") -> List[Dict[str, Any]]:
    """
    Convenience function to get features from backend.
    
    Args:
        base_url: The base URL of your backend API
        
    Returns:
        List of feature dictionaries in the expected format
    """
    client = BackendClient(base_url)
    return client.get_features()

# Example usage:
if __name__ == "__main__":
    # Test the backend client
    features = get_features_from_backend()
    print(f"Received {len(features)} features from backend")
    for feature in features:
        print(f"- {feature['name']}: {feature['short_desc']}") 