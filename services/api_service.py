"""
Service for communicating with a backend API to fetch feature data.
"""
import requests

def fetch_features_from_api(api_url: str, timeout: int = 10) -> list:
    """
    Fetches a list of features from the specified API endpoint.

    Args:
        api_url: The URL of the backend API.
        timeout: Request timeout in seconds (default: 10).

    Returns:
        A list of feature dictionaries.

    Raises:
        requests.exceptions.RequestException: If the network request fails.
        requests.exceptions.Timeout: If the request times out.
        requests.exceptions.ConnectionError: If connection to server fails.
    """
    response = requests.get(api_url, timeout=timeout)
    response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
    return response.json() 