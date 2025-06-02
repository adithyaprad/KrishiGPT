# Multilingual Farmer Assistant

A comprehensive AI-powered assistant designed to help farmers with agricultural information and weather forecasts in multiple Indian languages.

## 🌟 Features

- **Multilingual Support**: Understands and responds in 11 Indian languages
- **Weather Information**: Provides detailed weather forecasts for any location
- **Agricultural Knowledge**: Offers farming advice, crop management techniques, and more
- **Natural Language Processing**: Understands queries in natural language
- **Seamless Translation**: Automatically detects language and translates responses

## 🗣️ Supported Languages

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

## 🛠️ Technology Stack

- **Google ADK**: For building the agent pipeline
- **Google Gemini**: For language understanding and generation
- **SarvamAI**: For specialized agricultural knowledge and Indian language translation
- **OpenWeatherMap API**: For weather forecasts
- **Python**: Core programming language

## 📋 Prerequisites

- Python 3.8 or higher
- Google API key (for Gemini models)
- SarvamAI API key (for translation and agricultural knowledge)

## 🚀 Installation

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
4. Create a `.env` file in the project root with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SARVAM_API_KEY=your_sarvam_api_key_here
   ```

## 💻 Usage

### Basic Usage

```python
from agent import call_agent

# Ask about weather in English
response = call_agent("What's the weather like in Mumbai today?")
print(response)

# Ask about farming in Hindi
response = call_agent("मुझे फसलों की सिंचाई के बारे में जानकारी चाहिए")
print(response)
```

### Example Queries

#### Weather Queries:
- "What's the weather like in Mumbai today?"
- "Will it rain in Bangalore tomorrow?"
- "आज दिल्ली में तापमान कितना है?" (What's the temperature in Delhi today?)

#### Farming Queries:
- "How to protect tomato plants from pests?"
- "Best time to plant wheat in Punjab?"
- "ಕರ್ನಾಟಕದಲ್ಲಿ ರಾಗಿ ಬೆಳೆಯಲು ಯಾವ ಮಣ್ಣು ಉತ್ತಮ?" (Which soil is best for growing ragi in Karnataka?)

## 🧠 System Architecture

The system uses a sequential pipeline of specialized agents:

1. **Language Detection Agent**: Identifies the language of the user's query
2. **Translation Agent**: Translates the query to English
3. **Response Router Agent**: 
   - Analyzes if the query is about weather or farming
   - Routes to appropriate specialized agent
4. **Weather Agent**: For weather queries, extracts location and fetches forecast
5. **Farming Agent**: For farming queries, uses SarvamAI to provide agricultural information
6. **Final Response Agent**: Translates the response back to the user's original language

## 🔑 API Keys

This project requires two API keys:

1. **Google API Key**: For accessing Gemini models
   - Sign up at [Google AI Studio](https://makersuite.google.com/)
   - Create an API key and add it to your `.env` file

2. **SarvamAI API Key**: For translation and agricultural knowledge
   - Sign up at [SarvamAI](https://www.sarvam.ai/)
   - Create an API key and add it to your `.env` file

> **Note**: The project includes a default OpenWeatherMap API key for demonstration purposes. For production use, it's recommended to replace it with your own key.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Google ADK](https://github.com/google/agents-sdk) for the agent framework
- [SarvamAI](https://www.sarvam.ai/) for translation and agricultural knowledge
- [OpenWeatherMap](https://openweathermap.org/) for weather data 