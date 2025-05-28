# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file in project root
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Retrieve OpenAI API key from environment
try:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
except KeyError:
    OPENAI_API_KEY = None

# Retrieve Telegram Bot Token from environment
try:
    TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
except KeyError:
    TELEGRAM_BOT_TOKEN = None


