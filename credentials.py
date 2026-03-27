import os

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
    OPENAI_TOKEN: str = os.getenv("OPENAI_TOKEN")
    OPENAI_CLIENT = AsyncOpenAI(api_key=OPENAI_TOKEN)

config = Config()