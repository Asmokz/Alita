import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = "https://api.mistral.ai/v1/chat/completions"

# Modèle conversationnel principal
MISTRAL_MODEL_CHAT = "mistral-small-2506"
# Modèle plus petit/rapide pour la classification d'intentions
MISTRAL_MODEL_INTENT = "mistral-tiny"

# Historique de conversation pour la partie chat
conversation_history = [
    {
        "role": "system",
        "content": (
            "Je m'appelle Colin et je suis fan de spiderman. "
            "Tu es Alita, un assistant vocal personnel, rapide, clair et toujours amical. "
            "Réponds de manière concise, naturelle, sans trop de formalisme."
        )
    }
]


def call_mistral(model: str, messages: list) -> str:
    """Wrapper générique pour appeler Mistral API"""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 150,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(MISTRAL_BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Mistral API Error {response.status_code}: {response.text}")


def detect_intent_and_entities(user_input: str) -> str:
    """Demande au modèle tiny de classer l'intention"""
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un classifieur d'intentions et extracteur d'entités. "
                "Analyse la phrase donnée et renvoie un JSON avec deux clés : "
                "'intent' et 'entities'. "
                "Intent possible : [weather, system, mistral, exit, greeting, time, spotify, open_app, unknown]. "
                "Pour 'weather', l'entité clé est 'city'. "
                "Pour 'spotify', l'entité clé est 'track' ou 'artist'. "
                "Si aucune ville n'est trouvée, mets null. "
                "Réponds uniquement avec du JSON valide, sans texte autour."
            )
        },
        {"role": "user", "content": user_input}
    ]
    try:
        intent = call_mistral(MISTRAL_MODEL_INTENT, messages)
        print("Detected intent response:", intent)  # Debug print
        parsed = json.loads(intent)
        return parsed
    except json.JSONDecodeError:
        # En cas d'erreur de parsing, retourne unknown
        return {"intent": "unknown", "entities": {}}
    except Exception as e:
        raise e


def ask_mistral(user_input: str) -> str:
    """Route l'input soit vers une fonction dédiée, soit vers la conversation"""
    intent = detect_intent_and_entities(user_input)

    if intent == "meteo":
        # Exemple : tu pourrais ici appeler ta fonction météo
        return f"Je détecte une demande météo : '{user_input}'"
    elif intent == "system":
        # Exemple : tu pourrais renvoyer les stats CPU/GPU
        return f"Je détecte une demande système : '{user_input}'"
    elif intent == "conversation":
        # Ajouter dans l'historique et continuer la discussion
        conversation_history.append({"role": "user", "content": user_input})
        reply = call_mistral(MISTRAL_MODEL_CHAT, conversation_history)
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    else:
        return "Désolé, je n'ai pas compris ton intention."


