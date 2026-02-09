# KrishiGPT

A comprehensive AI-powered assistant designed to help farmers with agricultural information and weather forecasts in multiple Indian languages.

## Features

- **Multilingual Support**: Understands and responds in 11 Indian languages
- **Weather Information**: Provides detailed weather forecasts for any location
- **Agricultural Knowledge**: Offers farming advice, crop management techniques, and more
- **Government Statistics**: Fetches official MoSPI datasets via MCP tools
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
- **SarvamAI**: For specialized indic knowledge and Indian language translation
- **OpenWeatherMap API**: For weather forecasts
- **moSOPI MCP**: For goverment statistical data
- **Mandi API**: For real time accurate commodity prices
- **Python**: Core programming language

## Project Structure

```
├── src
│   └── krishigpt
│       ├── agents
│       │   ├── __init__.py
│       │   ├── farming_agent.py
│       │   ├── market_agent.py
│       │   ├── translation_agent.py
│       │   └── weather_agent.py
│       ├── tools
│       │   ├── __init__.py
│       │   ├── location.py
│       │   ├── market.py
│       │   ├── sarvam.py
│       │   ├── translation.py
│       │   └── weather.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── agent.py
│       ├── config.py
│       └── evalset03ac12.evalset.json
├── .gitignore
├── LICENSE
├── README.md
├── __init__.py
├── agent.py
├── env.example
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
   MOSPI_MCP_URL=https://mcp.mospi.gov.in
   ```

## Usage

### Basic Usage

```python
from krishigpt.agent import call_agent

# Ask about weather in English
response = call_agent("Which vegetable increased by more than 20% compared to last year ?")
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

#### Government Data Queries:
- "Which vegetable increased by more than 20% compared to last year ?"
- "What is the wholesale price index of wheat in the latest year?"
- "எந்த பருப்பு வகைகளின் விலை மிக அதிகமாக வளர்ச்சி அடைந்துள்ளது?" (Which pulses have seen the highest growth in price?)

### Commodity / Mandi Price Queries

- “What is the current mandi price of onions in Maharashtra?”
- “What's the soybean prices in Madhya Pradesh mandis.”
- "હાલ ઘઉં માટે કયું રાજ્ય સૌથી વધુ MSP કિંમત ઓફર કરી રહ્યું છે?" (Which state is offering the highest MSP price for wheat currently?)


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

4. **MoSPI MCP (optional)**: For government statistics via MCP
   - Set `MOSPI_MCP_URL` to the MoSPI MCP endpoint

> **Note**: `env.example` is included as a template for required environment variables.
