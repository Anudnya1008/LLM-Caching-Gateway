import os
from dotenv import load_dotenv
from google import genai
import random
from google.genai.errors import ServerError
import time


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(
    api_key=API_KEY,
    http_options={"timeout": 300_000}
)

def generate_llm_response(question: str) -> str:

    max_attempts = 2
    for attempt in range(max_attempts):
        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=question
            )

            if not response.text:
                raise RuntimeError("Gemini returned no text response")

            return response.text
        except ServerError as error:
            if error.code not in (503, 504):
                raise

            if attempt == max_attempts - 1:
                raise

            wait_time = (2 ** attempt) + random.uniform(0, 1)

            print(
                f"Gemini unavailable. "
                f"Retrying in {wait_time:.2f} seconds..."
            )

            time.sleep(wait_time)



# import time

# def generate_llm_response(question:str):
#     time.sleep(2)

#     return f"This is a simulated response for: {question}"



