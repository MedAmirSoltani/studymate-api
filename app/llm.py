from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

def get_client():
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

def ask_llm(context: str, question: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful study assistant. Answer the question using ONLY the context provided. If the answer is not in the context, say 'I don't know based on the provided documents'."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
        temperature=0.3,
        max_tokens=1024
    )
    return response.choices[0].message.content