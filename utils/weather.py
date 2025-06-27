import requests

WEATHER_API_KEY = "b4f91a8e2fc049b4aa9103537252706"  # Replace with your actual API key if needed
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def fetch_current_weather(location="Cairo"):
    """
    Fetch current weather data for the given location from WeatherAPI.com.
    :param location: City name or lat,lon (e.g., "Cairo" or "30.0444,31.2357")
    :return: dict with weather data or None on failure
    """
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "aqi": "no"
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None 