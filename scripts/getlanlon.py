import requests
import json
import sys
import os

def get_lat_lon(location="Bangalore,KA,IN"):
    """
    Fetch latitude and longitude for a given location using OpenWeatherMap API
    
    Args:
        location (str): Location in format "City,State,Country" (default: "Bangalore,KA,IN")
    
    Returns:
        dict: Dictionary containing latitude, longitude and status information
    """
    # API endpoint for geocoding
    url = "http://api.openweathermap.org/geo/1.0/direct"
    
    # API key - for production, replace with your own key or use environment variable
    # Example: api_key = os.getenv("OPENWEATHER_API_KEY", "default_key_here")
    api_key = "504cf7be2db8659dee10b036b1812848"  # Default key for demo purposes only
    
    # Parameters
    params = {
        "q": location,
        "limit": 1,
        "appid": api_key
    }
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Extract lat and lon from the first item
        if data and isinstance(data, list):
            location_data = data[0]
            latitude = location_data.get("lat")
            longitude = location_data.get("lon")
            return {
                "status": "success",
                "location": location,
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            print("No location data found.", file=sys.stderr)
            return {
                "status": "error",
                "message": f"Could not find coordinates for location: {location}",
                "latitude": None,
                "longitude": None
            }
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location data: {e}", file=sys.stderr)
        return {
            "status": "error",
            "message": f"Error retrieving coordinates: {str(e)}",
            "latitude": None,
            "longitude": None
        }
    except json.JSONDecodeError:
        print("Error parsing JSON response.", file=sys.stderr)
        return {
            "status": "error",
            "message": "Error parsing response from API",
            "latitude": None,
            "longitude": None
        }

# Example usage
if __name__ == "__main__":
    # Check if location is provided as command-line argument or via stdin
    location = "Bangalore,KA,IN"  # Default location
    
    if len(sys.argv) > 1:
        # Get location from command-line argument
        location = sys.argv[1]
    elif not sys.stdin.isatty():
        # Get location from stdin
        location = sys.stdin.read().strip()
    
    result = get_lat_lon(location)
    # Print the result as JSON to stdout
    print(json.dumps(result))