import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-2506"

# Historique de conversation : à stocker dynamiquement si besoin
conversation_history = [
    {
        "role": "system",
        "content": (
            "Je m'appelle Colin et je suis fan de spiderman"
            "Tu es Alita, un assistant vocal personnel, rapide, clair et toujours amical. "
            "Réponds de manière concise, naturelle, sans trop de formalisme. "
            "Tu es capable de répondre à des questions générales, techniques ou personnelles."
        )
    }
]

def ask_mistral(user_input: str) -> str:
    # Ajouter le message utilisateur à l’historique
    conversation_history.append({"role": "user", "content": user_input})

    # Préparer la requête
    payload = {
        "model": MISTRAL_MODEL,
        "messages": conversation_history,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 300,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(MISTRAL_BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        # Ajouter la réponse de l’assistant à l’historique
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    else:
        raise Exception(f"Mistral API Error {response.status_code}: {response.text}")
