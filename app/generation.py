from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()


def generate_answer(question, context):

    prompt = f"""
You are a Spring Boot documentation assistant.

Answer the user's question using only the provided context.

If the answer cannot be found in the context, say:
"I couldn't find the answer in the provided Spring Boot documentation."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text