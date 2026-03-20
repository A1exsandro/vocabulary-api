import os
import requests
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_sentences(word: str):

    prompt = f"""
    You are an English vocabulary assistant.

    Task:
    1. Check if the word "{word}" is a valid English word.
    2. If it is misspelled, suggest the correct spelling.
    3. Provide the Portuguese translation.
    4. Create 3 very simple sentences using the correct word.

    Return ONLY JSON.

    {{
      "valid": true,
      "correct_word": "",
      "translation": "",
      "sentences": []
    }}
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemma-3n-e2b-it:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    data = response.json()

    content = data["choices"][0]["message"]["content"]

    # remove markdown se existir
    content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)
