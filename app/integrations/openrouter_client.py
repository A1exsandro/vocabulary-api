import json
import os

import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_sentences(word: str):
    prompt = f"""
    You are an English vocabulary assistant.

    Task:
    1. Check if the word "{word}" is a valid English word.
    2. If it is misspelled, suggest the correct spelling.
    3. Provide the Portuguese translation for the corrected word.
    4. Create 3 very simple English sentences using the corrected word.
    5. Provide a Portuguese translation for each sentence.

    Return ONLY JSON with this shape:

    {{
      "valid": true,
      "correct_word": "",
      "translation": "",
      "sentences": [
        {{"english": "", "portuguese": ""}}
      ]
    }}
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemma-3n-e2b-it:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        },
    )

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Remove markdown wrappers if present.
    content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)
