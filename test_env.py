from dotenv import load_dotenv
import os

load_dotenv()

print("ENV VALUE:", os.getenv("OPENWEATHER_API_KEY"))