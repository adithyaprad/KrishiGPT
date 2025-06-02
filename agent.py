from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from typing import Dict, Any, List, Optional
from google.adk.tools import FunctionTool
from google.adk.agents.base_agent import BaseAgent
from sarvamai import SarvamAI
import os
import re

# Import the response agent
from .scripts.response_agent import create_response_agent

"""
Multilingual Farmer Assistant Agent Pipeline

This system provides a complete end-to-end pipeline for handling multilingual queries about farming:

1. Language Detection Agent: Identifies the language of the user's query from 11 Indian languages
2. Translation Agent: Translates the user's query from the detected language to English
3. Response Agent: 
   - Analyzes the query and determines if it's about weather
   - For weather queries, uses specialized tools to get weather information
   - For non-weather queries, provides a direct response
4. Final Response Agent: Translates the English response back to the user's original language

The system provides responses in both English and the user's original language.
The SarvamAI translation API is used for both translation steps, ensuring accurate
translations between Indian languages and English.

Supported languages:
- en-IN: English
- hi-IN: Hindi
- bn-IN: Bengali
- gu-IN: Gujarati
- kn-IN: Kannada
- ml-IN: Malayalam
- mr-IN: Marathi
- od-IN: Odia
- pa-IN: Punjabi
- ta-IN: Tamil
- te-IN: Telugu
"""

# App configuration
APP_NAME = "translator_assistant_app"
USER_ID = "user_01"
SESSION_ID = "translation_session_01"
GEMINI_MODEL = "gemini-2.0-flash-exp"


# Language Detection Agent - Detects the language of the user's query
language_detection_agent = LlmAgent(
    name="LanguageDetectionAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Language Detection Agent.
    Your task is to identify which language the user's query is written in.
    
    Only consider the following language options:
    en-IN: English
    hi-IN: Hindi
    bn-IN: Bengali
    gu-IN: Gujarati
    kn-IN: Kannada
    ml-IN: Malayalam
    mr-IN: Marathi
    od-IN: Odia
    pa-IN: Punjabi
    ta-IN: Tamil
    te-IN: Telugu
    
    Return ONLY the language code (e.g., "hi-IN", "en-IN", etc.) without any additional text or explanation.
    If you're unsure, default to "en-IN".
    """,
    description="Detects the language of the user's query.",
    output_key="detected_language"
)

# Translation tool using SarvamAI
def translate_text(
    text: str, 
    source_language_code: str = "en-IN",
    target_language_code: str = "en-IN",
    speaker_gender: str = "Male", 
    mode: str = "classic-colloquial"
) -> Dict[str, Any]:
    """
    Translates text using SarvamAI API.
    
    Args:
        text: The input text to translate
        source_language_code: Source language code (e.g., "hi-IN", "en-IN")
        target_language_code: Target language code (e.g., "hi-IN", "en-IN")
        speaker_gender: Gender of speaker ("Male" or "Female")
        mode: Translation mode ("formal", "classic-colloquial", or "modern-colloquial")
    
    Returns:
        Dict with translated text and status
    """
    try:
        client = SarvamAI(
            api_subscription_key=os.getenv("SARVAM_API_KEY")
        )
        
        response = client.text.translate(
            input=text,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            speaker_gender=speaker_gender,
            mode=mode
        )
        
        return {
            "status": "success",
            "translated_text": response.translated_text
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

# Create the translation tool
translation_tool = FunctionTool(func=translate_text)

# Agent 2: Translation Agent - Translates user queries to English using detected language
translation_agent = LlmAgent(
    name="TranslationAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Translation Agent.
    Your task is to translate the user's query to English using the translation tool.
    Use the language code provided in the session state under the key 'detected_language' as the source_language_code parameter when calling the translation tool.
    Access the detected language code from the session state and pass it explicitly to the translation tool.
    
    For example, if the detected language is "hi-IN", you should call the translation tool with:
    translate_text(
        text=user_query,
        source_language_code="hi-IN",
        speaker_gender="Male",
        mode="classic-colloquial"
    )
    
    If the query is already in English (detected_language is 'en-IN'), still use the translation tool for consistency.
    Output only the translated text without additional explanations.
    """,
    description="Translates user queries to English using the translation tool with detected language.",
    tools=[translation_tool],
    output_key="translated_query"
)

# Create the response agent
response_agent = create_response_agent(model=GEMINI_MODEL)

# Agent 4: Final Response Agent - Translates the response back to the user's original language
final_response_agent = LlmAgent(
    name="FinalResponseAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Translation Agent for responses.
    Your task is to translate the English response back to the user's original language.
    
    1. Get the English response from the session state under the key 'english_response'.
    2. Get the user's original language code from the session state under the key 'detected_language'.
    3. Use the translation tool to translate the response to the user's original language.
    
    For example, if the detected language is "hi-IN", you should call the translation tool with:
    translate_text(
        text=english_response,
        source_language_code="en-IN",
        target_language_code="hi-IN",
        speaker_gender="Male",
        mode="classic-colloquial"
    )
    
    If the original language was English (detected_language is 'en-IN'), just return the English response as is.
    Output only the translated response without additional explanations.
    """,
    description="Translates the English response back to the user's original language.",
    tools=[translation_tool],
    output_key="final_response"
)

# Create the sequential agent pipeline
root_agent = SequentialAgent(
    name="MultilingualFarmerAssistantPipeline",
    sub_agents=[
        language_detection_agent, 
        translation_agent, 
        response_agent, 
        final_response_agent
    ]
)

# Set up the session service and runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

def call_agent(query):
    """
    Process a user query through the agent pipeline.
    
    Args:
        query: The user's query text
        
    Returns:
        The agent's response as a string, including both English and translated responses
    """
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    # For debugging - will show each agent's output
    print("\nProcessing pipeline for query:", query)
    
    responses = {}
    for event in events:
        # Print out intermediary responses for debugging
        if hasattr(event, 'output_key') and event.output_key:
            output_value = event.content.parts[0].text if hasattr(event.content, 'parts') else event.content
            print(f"Agent '{event.agent_name}' output ({event.output_key}):", output_value)
            
            # Store each key output for final response formatting
            responses[event.output_key] = output_value
            
            # Debug logging for Sarvam LLM integration
            if event.agent_name == "ResponseAgent" and event.output_key == "english_response":
                is_weather = "Weather query detected" if "weather" in output_value.lower() or "temperature" in output_value.lower() else "Non-weather query - using Sarvam LLM"
                print(f"Query type: {is_weather}")
            
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Final Response: ", final_response)
    
    # Format response to include both English and translated text
    formatted_response = []
    
    # Language mapping dictionary for all language codes
    language_names = {
        'en-IN': 'English', 'hi-IN': 'Hindi', 'bn-IN': 'Bengali', 
        'gu-IN': 'Gujarati', 'kn-IN': 'Kannada', 'ml-IN': 'Malayalam', 
        'mr-IN': 'Marathi', 'od-IN': 'Odia', 'pa-IN': 'Punjabi', 
        'ta-IN': 'Tamil', 'te-IN': 'Telugu'
    }
    
    # Add detected language information
    if 'detected_language' in responses:
        language_code = responses['detected_language']
        language_name = language_names.get(language_code, language_code)
        formatted_response.append(f"Detected Language: {language_name} ({language_code})")
    
    # Add English response
    if 'english_response' in responses:
        formatted_response.append(f"\nEnglish Response:\n{responses['english_response']}")
    
    # Add translated response
    if 'final_response' in responses and responses.get('detected_language') != 'en-IN':
        language_code = responses.get('detected_language')
        language_name = language_names.get(language_code, language_code)
        formatted_response.append(f"\n{language_name} Response:\n{responses['final_response']}")
    
    return "\n".join(formatted_response)

def test_pipeline():
    """
    Test the agent pipeline with a sample query.
    """
    test_query = "What's the weather like in Mumbai today?"
    response = call_agent(test_query)
    print("\nFinal formatted response:")
    print(response)

if __name__ == "__main__":
    test_pipeline()