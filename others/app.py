import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client using the API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_prompt(prompt_text):
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        input=prompt_text
    )
    # The Responses API returns output in output_text or structured output
    # We'll print whatever is available
    return getattr(response, "output_text", None) or response.output

if __name__ == "__main__":
    prompt = "Tell me a fun fact about space."
    answer = ask_prompt(prompt)
    print("Response:", answer)
