import json
import os

import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemma-3n-e2b-it:free"


def _request_json(prompt: str) -> dict:
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
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
    content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)


def generate_sentences(word: str):
    prompt = f"""
    You are an English vocabulary assistant.

    Task:
    1. Check if the word \"{word}\" is a valid English word.
    2. If it is misspelled, suggest the correct spelling.
    3. Provide the Portuguese translation for the corrected word.
    4. Create 3 very simple English sentences using the corrected word.
    5. Provide a Portuguese translation for each sentence.
    6. Classify the corrected word into exactly one grammatical class using one of these slugs:
       substantivos, pronomes, verbos, adjetivos, adverbios, preposicoes, conjuncoes, interjeicoes, artigos.

    Return ONLY JSON with this shape:

    {{
      \"valid\": true,
      \"correct_word\": \"\",
      \"translation\": \"\",
      \"grammar_class_slug\": \"\",
      \"sentences\": [
        {{\"english\": \"\", \"portuguese\": \"\"}}
      ]
    }}
    """

    return _request_json(prompt)


def generate_short_text(topic: str):
    prompt = f"""
    You are an English writing assistant.

    Task:
    1. Write one short beginner-friendly English text about \"{topic}\".
    2. The text should be 3 to 5 short sentences.
    3. Provide a natural Portuguese translation of the whole text.

    Return ONLY JSON with this shape:

    {{
      \"english\": \"\",
      \"portuguese\": \"\"
    }}
    """

    return _request_json(prompt)
