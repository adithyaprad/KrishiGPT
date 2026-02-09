# KrishiGPT

A comprehensive AI-powered assistant designed to help farmers with agricultural information and weather forecasts in multiple Indian languages.

## Project Demo

https://github.com/user-attachments/assets/acb3e669-224a-43d5-ac9b-852304626ea3

## Flow of Events
![Image](https://github.com/user-attachments/assets/94e8da1b-c417-4bf1-9c0c-81fec31ee56c)

## Agent Architechture 
![Image](https://github.com/user-attachments/assets/0b52ad16-c25c-4736-ab20-5f4d1dc2681b)

## Features

- **Multilingual Support**: Understands and responds in 11 Indian languages
- **Weather Information**: Provides detailed weather forecasts for any location
- **Agricultural Knowledge**: Offers farming advice, crop management techniques, and more
- **Natural Language Processing**: Understands queries in natural language
- **Seamless Translation**: Automatically detects language and translates responses

## Supported Languages

- English (en-IN)
- Hindi (hi-IN)
- Bengali (bn-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Marathi (mr-IN)
- Odia (od-IN)
- Punjabi (pa-IN)
- Tamil (ta-IN)
- Telugu (te-IN)

## Technology Stack

- **Google ADK**: For building the agent pipeline
- **Google Gemini**: For language understanding and generation
- **SarvamAI**: For specialized agricultural knowledge and Indian language translation
- **OpenWeatherMap API**: For weather forecasts
- **Python**: Core programming language

## Project Structure

```
├── src
│   └── krishigpt
│       ├── agents
│       │   ├── __init__.py
│       │   └── response_agent.py
│       ├── tools
│       │   ├── __init__.py
│       │   ├── location.py
│       │   ├── sarvam.py
│       │   ├── translation.py
│       │   └── weather.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── agent.py
│       └── config.py
├── .gitignore
├── LICENSE
├── README.md
├── __init__.py
├── agent.py
├── env.example
├── mcpdocs.md
├── pyproject.toml
└── requirements.txt
```

## Prerequisites

- Python 3.8 or higher
- Google API key (for Gemini models)
- SarvamAI API key (for translation and agricultural knowledge)

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install the package in editable mode (recommended for development):
   ```bash
   pip install -e .
   ```
5. Create a `.env` file in the project root with your API keys (see `env.example`):
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SARVAM_API_KEY=your_sarvam_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

## Usage

### Basic Usage

```python
from krishigpt.agent import call_agent

# Ask about weather in English
response = call_agent("What's the weather like in Mumbai today?")
print(response)

# Ask about farming in Hindi
response = call_agent("मुझे फसलों की सिंचाई के बारे में जानकारी चाहिए")
print(response)

```
### CLI Demo

Run a quick demo pipeline:
```bash
python -m krishigpt
```
### Web usage - ADK web

1. Run `adk web` from the project root and point it to the agents directory:
```bash
adk web src
```
Then select the `krishigpt` app in the UI.


### Example Queries

#### Weather Queries:
- "What's the weather like in Mumbai today?"
- "Will it rain in Bangalore tomorrow?"
- "आज दिल्ली में तापमान कितना है?" (What's the temperature in Delhi today?)

#### Farming Queries:
- "How to protect tomato plants from pests?"
- "Best time to plant wheat in Punjab?"
- "ಕರ್ನಾಟಕದಲ್ಲಿ ರಾಗಿ ಬೆಳೆಯಲು ಯಾವ ಮಣ್ಣು ಉತ್ತಮ?" (Which soil is best for growing ragi in Karnataka?)

## System Architecture

The system uses a sequential pipeline of specialized agents:

1. **Language Detection Agent**: Identifies the language of the user's query
2. **Translation Agent**: Translates the query to English
3. **Response Router Agent**: 
   - Analyzes if the query is about weather or farming
   - Routes to appropriate specialized agent
4. **Weather Agent**: For weather queries, extracts location and fetches forecast
5. **Farming Agent**: For farming queries, uses SarvamAI to provide agricultural information
6. **Final Response Agent**: Translates the response back to the user's original language

## API Keys

This project requires two API keys:

1. **Google API Key**: For accessing Gemini models
   - Sign up at [Google AI Studio](https://makersuite.google.com/)
   - Create an API key and add it to your `.env` file

2. **SarvamAI API Key**: For translation and agricultural knowledge
   - Sign up at [SarvamAI](https://www.sarvam.ai/)
   - Create an API key and add it to your `.env` file

3. **OpenWeatherMap API Key**: For weather forecasts
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Create an API key and add it to your `.env` file

> **Note**: `env.example` is included as a template for required environment variables.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Google ADK](https://github.com/google/agents-sdk) for the agent framework
- [SarvamAI](https://www.sarvam.ai/) for translation and agricultural knowledge
- [OpenWeatherMap](https://openweathermap.org/) for weather data 
