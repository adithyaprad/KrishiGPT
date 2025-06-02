from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool
import re
import json
import subprocess
import sys
import os
from typing import Dict, Any, Optional
from openai import OpenAI

def is_weather_query(query: str) -> Dict[str, Any]:
    """
    Determines if a query is asking about weather.
    
    Args:
        query: The user's query text
        
    Returns:
        Dict with whether the query is about weather and the location if detected
    """
    query = query.lower()
    
    # Define weather-related keywords
    weather_keywords = [
        "weather", "temperature", "forecast", "rain", "sunny", "cloudy", 
        "humidity", "climate", "precipitation", "hot", "cold", "warm", "cool"
    ]
    
    # Check if any weather keyword is in the query
    is_weather = any(keyword in query for keyword in weather_keywords)
    
    # Try to extract location using a simple pattern
    location_match = None
    if is_weather:
        # Look for patterns like "weather in X", "temperature at X", etc.
        patterns = [
            r"(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)",
            r"(?:weather|temperature|forecast|climate)\s+of\s+([A-Za-z\s,]+)",
            r"(?:how's|what's|what is)\s+(?:the|)\s+(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)",
            r"(?:how|what)\s+(?:is|are)\s+(?:the|)\s+(?:weather|temperature|forecast|climate)\s+(?:in|at|for|of)\s+([A-Za-z\s,]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                location_match = match.group(1).strip()
                break
    
    return {
        "is_weather_query": is_weather,
        "location": location_match if location_match else "Bangalore,KA,IN"  # Default to Bangalore if no location found
    }

def execute_getlanlon(location: str) -> Dict[str, Any]:
    """
    Execute the getlanlon.py script to get latitude and longitude for a location.
    
    Args:
        location: Location string in format "City,State,Country"
        
    Returns:
        Dict with the results from the script
    """
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to getlanlon.py
        script_path = os.path.join(current_dir, "getlanlon.py")
        
        # Execute the script as a subprocess with the location as an argument
        result = subprocess.run(
            [sys.executable, script_path, location],
            text=True,
            capture_output=True,
            check=True
        )
        
        # Parse the JSON output
        output = json.loads(result.stdout)
        return output
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error executing getlanlon.py: {e.stderr}",
            "latitude": None,
            "longitude": None
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Error parsing output from getlanlon.py",
            "latitude": None,
            "longitude": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "latitude": None,
            "longitude": None
        }

def execute_getweatherapi(location_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the getweatherapi.py script to get weather data using location data.
    
    Args:
        location_data: Dictionary with location data from getlanlon.py
        
    Returns:
        Dict with the weather data
    """
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to getweatherapi.py
        script_path = os.path.join(current_dir, "getweatherapi.py")
        
        # Convert location_data to JSON string
        location_data_json = json.dumps(location_data)
        
        # Execute the script as a subprocess with the location_data as input
        result = subprocess.run(
            [sys.executable, script_path],
            input=location_data_json,
            text=True,
            capture_output=True,
            check=True
        )
        
        # Parse the JSON output
        output = json.loads(result.stdout)
        return output
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error executing getweatherapi.py: {e.stderr}",
            "weather_data": None
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Error parsing output from getweatherapi.py",
            "weather_data": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "weather_data": None
        }

def use_sarvam_llm(query: str) -> Dict[str, Any]:
    """
    Process a non-weather query using the Sarvam LLM API.
    
    Args:
        query: The user's query text
        
    Returns:
        Dict with the response from Sarvam LLM
    """
    try:
        # Initialize the OpenAI client with Sarvam.ai base URL
        client = OpenAI(
            base_url="https://api.sarvam.ai/v1",
            api_key=os.getenv("SARVAM_API_KEY")
        )
        
        # Add farming context to the system message
        system_message = """
        You are a knowledgeable farming assistant that helps farmers with their questions.
        Provide accurate, practical, and helpful information about:
        - Crop cultivation techniques and best practices
        - Pest and disease management
        - Soil health and fertilization
        - Water management and irrigation
        - Sustainable farming practices
        - Agricultural tools and equipment
        - Seasonal farming advice
        - Market trends and crop selection
        
        Keep your responses concise, practical, and tailored to the farmer's specific question.
        """
        
        # Send the query to Sarvam LLM
        response = client.chat.completions.create(
            model="sarvam-m",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        print(f"Sarvam LLM Response for query '{query}': {response_content[:100]}...")
        
        return {
            "status": "success",
            "response": response_content
        }
    except Exception as e:
        error_message = str(e)
        print(f"Error using Sarvam LLM: {error_message}")
        
        return {
            "status": "error",
            "message": f"Error using Sarvam LLM: {error_message}",
            "response": "I'm sorry, I couldn't process your farming query at the moment. Please try again later or ask a different question about farming practices."
        }

# Create the tools
weather_detection_tool = FunctionTool(func=is_weather_query)
getlanlon_tool = FunctionTool(func=execute_getlanlon)
getweatherapi_tool = FunctionTool(func=execute_getweatherapi)
sarvam_llm_tool = FunctionTool(func=use_sarvam_llm)

def create_response_agent(model: str = "gemini-2.0-flash-lite") -> LlmAgent:
    """
    Create and return a Response Agent that handles weather queries using the simplified tools
    and non-weather queries using the Sarvam LLM.
    
    Args:
        model (str): The model to use for the agent
        
    Returns:
        LlmAgent: The configured response agent
    """
    response_agent = LlmAgent(
        name="ResponseAgent",
        model=model,
        instruction="""You are a helpful assistant for farmers that can provide weather information and farming advice.
        
        When you receive a query, follow these steps:
        
        1. First, get the translated query from the session state under the key 'translated_query'.
        2. Use the is_weather_query tool to determine if the query is about weather.
        
        If the query IS about weather:
        1. Extract the location from the is_weather_query tool's response.
        2. Use the execute_getlanlon tool to get the latitude and longitude for the location.
        3. Use the execute_getweatherapi tool with the location data to get the weather forecast.
        4. Summarize the weather information in a friendly, conversational format.
        5. Include all important details like temperature, conditions, humidity, and wind speed.
        
        If the query is NOT about weather:
        1. Use the use_sarvam_llm tool with the translated query to get a response from the Sarvam LLM.
        2. Check the status of the Sarvam LLM response:
           - If status is "success", use the "response" field from the result
           - If status is "error", provide a fallback response explaining the issue
        3. Format the response in a friendly, conversational manner.
        
        Your response will be translated back to the user's original language in the next step.
        """,
        description="Handles user queries and provides weather information or farming advice using specialized tools.",
        tools=[weather_detection_tool, getlanlon_tool, getweatherapi_tool, sarvam_llm_tool],
        output_key="english_response"
    )
    
    return response_agent 