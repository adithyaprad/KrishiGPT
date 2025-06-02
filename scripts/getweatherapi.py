import requests
import json
import sys
import os

def get_weather_forecast(location_data=None, api_key=None):
    """
    Fetch weather forecast data for a location using data from getlanlon.py
    
    Args:
        location_data (dict): Dictionary containing latitude, longitude and location information
        api_key (str): OpenWeatherMap API key
        
    Returns:
        dict: Processed weather data with summary
    """
    # If no API key is provided, use the default one (for demo purposes only)
    # For production, use your own API key or set it as an environment variable
    if api_key is None:
        api_key = os.getenv("OPENWEATHER_API_KEY", "504cf7be2db8659dee10b036b1812848")
    
    # Check if location_data is provided and valid
    if not location_data or not isinstance(location_data, dict):
        return {
            "status": "error",
            "message": "Invalid or missing location data",
            "weather_data": None
        }
    
    # Check if location_data has valid coordinates
    lat = location_data.get("latitude")
    lon = location_data.get("longitude")
    location = location_data.get("location", "Unknown location")
    
    if lat is None or lon is None:
        return {
            "status": "error",
            "message": f"Missing coordinates for location: {location}",
            "weather_data": None
        }
    
    # Define the API endpoint and parameters
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Get the list of weather entries
        weather_list = data.get('list', [])
        
        if not weather_list:
            return {
                "status": "error",
                "message": "No weather data found",
                "weather_data": None
            }
            
        # Find the date (YYYY-MM-DD) of the first entry
        first_date = weather_list[0]['dt_txt'].split(' ')[0]
        
        # Filter entries for only the first date
        first_day_data = [entry for entry in weather_list if entry['dt_txt'].startswith(first_date)]
        
        # Process data for the day
        temps = [entry['main']['temp'] - 273.15 for entry in first_day_data]  # Convert from Kelvin to Celsius
        min_temp = round(min(temps), 1)
        max_temp = round(max(temps), 1)
        avg_temp = round(sum(temps) / len(temps), 1)
        
        # Get weather conditions
        weather_conditions = []
        for entry in first_day_data:
            for condition in entry['weather']:
                if condition['main'] not in weather_conditions:
                    weather_conditions.append(condition['main'])
        
        # Get humidity, pressure, wind speed averages
        humidity_avg = sum(entry['main']['humidity'] for entry in first_day_data) / len(first_day_data)
        pressure_avg = sum(entry['main']['pressure'] for entry in first_day_data) / len(first_day_data)
        
        # Check if 'wind' and 'speed' keys exist in each entry
        wind_speeds = [entry.get('wind', {}).get('speed', 0) for entry in first_day_data]
        wind_speed_avg = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 0
        
        # Create the summary
        city_name = data.get('city', {}).get('name', location)
        
        # Generate a human-readable summary text
        text_summary = f"Weather forecast for {city_name} on {first_date}:\n"
        text_summary += f"Temperature: {min_temp}°C to {max_temp}°C (avg: {avg_temp}°C)\n"
        text_summary += f"Conditions: {', '.join(weather_conditions)}\n"
        text_summary += f"Humidity: {round(humidity_avg, 1)}%\n"
        text_summary += f"Wind Speed: {round(wind_speed_avg, 1)} m/s\n"
        
        return {
            "status": "success",
            "message": "Successfully retrieved weather data",
            "location": city_name,
            "date": first_date,
            "temperature": {
                "min": min_temp,
                "max": max_temp,
                "average": avg_temp,
                "unit": "°C"
            },
            "weather_conditions": weather_conditions,
            "humidity": round(humidity_avg, 1),
            "wind_speed": round(wind_speed_avg, 1),
            "text_summary": text_summary
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}", file=sys.stderr)
        return {
            "status": "error",
            "message": f"Error fetching weather data: {e}",
            "weather_data": None
        }
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error processing weather data: {e}", file=sys.stderr)
        return {
            "status": "error",
            "message": f"Error processing weather data: {e}",
            "weather_data": None
        }

# Example usage
if __name__ == "__main__":
    try:
        # Read location data from stdin or use default
        if not sys.stdin.isatty():
            # Get location data from stdin as JSON
            input_data = sys.stdin.read().strip()
            location_data = json.loads(input_data)
        else:
            # Use default location data
            location_data = {
                "status": "success",
                "location": "Bangalore,KA,IN",
                "latitude": 12.9716,
                "longitude": 77.5946
            }
        
        # Get weather data
        weather_data = get_weather_forecast(location_data)
        
        # Print the result as JSON to stdout
        print(json.dumps(weather_data))
        
    except json.JSONDecodeError as e:
        print(f"Error parsing input JSON: {e}", file=sys.stderr)
        print(json.dumps({
            "status": "error",
            "message": f"Error parsing input JSON: {e}",
            "weather_data": None
        }))
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(json.dumps({
            "status": "error",
            "message": f"Unexpected error: {e}",
            "weather_data": None
        }))