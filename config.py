import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROK_API_KEY")

GROQ_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1
MAX_TOKENS = 800
SIMILARITY_THRESHOLD = 0.85