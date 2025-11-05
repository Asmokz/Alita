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


def detect_intent_and_entities(user_input: str) -> dict:
    """Demande au modèle tiny de classer l'intention et extraire les entités, avec des actions précises."""
    messages = [
        {
            "role": "system",
            "content": (
            "Tu es un classifieur d'intentions et d'actions pour un assistant vocal. "
            "Ta tâche est d'analyser la phrase de l'utilisateur et de retourner UNIQUEMENT un JSON valide avec les clés suivantes : "
            "- 'intent' (obligatoire) : Choisis PARMI CES OPTIONS SEULEMENT : "
            "  [weather, system, mistral, exit, greeting, time, spotify, open_app, unknown]. "
            "- 'action' (obligatoire) : Choisis en fonction de l'intent et de la phrase. "
            "  Voici les actions possibles PAR INTENT : "
            "  - 'weather' : "
            "    - 'get_current' : pour la météo actuelle (ex: 'Quel temps fait-il à Paris ?'). "
            "    - 'get_forecast' : pour les prévisions (ex: 'Quel temps demain à Lyon ?'). "
            "  - 'system' : "
            "    - 'get_usage' : pour les stats système (RAM, CPU) (ex: 'Quelle est l'utilisation CPU ?'). "
            "    - 'shutdown' : pour éteindre (ex: 'Éteins l'ordinateur'). "
            "    - 'reboot' : pour redémarrer (ex: 'Redémarre le PC'). "
            "    - 'get_time' : pour l'heure (ex: 'Quelle heure est-il ?'). "
            "  - 'spotify' : "
            "    - 'play_track' : pour jouer une piste/artiste/album (ex: 'Joue Daft Punk'). "
            "    - 'pause' : pour mettre en pause (ex: 'Mets en pause'). "
            "    - 'resume' : pour reprendre (ex: 'Reprends la musique'). "
            "    - 'next_track' : pour passer à la piste suivante (ex: 'Musique suivante', 'Passe à la prochaine'). "
            "    - 'previous_track' : pour revenir à la piste précédente (ex: 'Musique précédente'). "
            "    - 'set_volume' : pour régler le volume (ex: 'Mets le volume à 50%'). "
            "    - 'search_track' : UNIQUEMENT pour chercher sans jouer (ex: 'Trouve des musiques de La Fouine'). "
            "  - 'mistral' : "
            "    - 'conversation' : pour une conversation libre (ex: 'Parlons de l'IA'). "
            "  - 'exit' : "
            "    - 'shutdown_assistant' : pour arrêter l'assistant (ex: 'Éteins-toi', 'Au revoir'). "
            "  - 'greeting' : "
            "    - 'greet' : pour saluer (ex: 'Bonjour', 'Salut'). "
            "  - 'time' : "
            "    - 'get_time' : pour l'heure (ex: 'Quelle heure est-il ?'). "
            "  - 'open_app' : "
            "    - 'open' : pour ouvrir une application (ex: 'Ouvre Firefox'). "
            "  - 'unknown' : "
            "    - 'default' : si l'intent n'est pas clair. "
            "- 'entities' (obligatoire) : Les entités extraites de la phrase. "
            "  - Pour 'weather' : 'city' (ville), 'country' (pays). "
            "  - Pour 'spotify' : 'artist', 'track', 'album', 'volume' (nombre entre 0 et 100). "
            "  - Pour 'system' : 'resource' (ex: 'CPU', 'RAM'). "
            "  - Pour 'open_app' : 'app_name' (nom de l'application). "
            "  - Si aucune entité n'est pertinente, laisse 'entities' vide ({}). "
            "- 'confidence' (optionnel) : Un score de confiance entre 0 et 1 pour la détection. "
            "- 'language' (optionnel) : La langue détectée (ex: 'fr'). "
            ""
            "REGLES STRICTES : "
            "1. Pour 'spotify' : "
            "   - Si la phrase contient 'suivante', 'prochaine', ou 'next' → 'next_track'. "
            "   - Si la phrase contient 'précédente', 'avant', ou 'previous' → 'previous_track'. "
            "   - Si la phrase contient 'pause' → 'pause'. "
            "   - Si la phrase contient 'reprends', 'reprendre', ou 'resume' → 'resume'. "
            "   - Si la phrase contient 'volume' → 'set_volume' + extraire le pourcentage. "
            "   - Si la phrase demande de jouer quelque chose → 'play_track' + entités. "
            "   - Ne JAMAIS utiliser 'search_track' pour des phrases comme 'musique suivante' ou 'pause'. "
            "2. Pour 'weather' : "
            "   - Si la phrase contient 'demain', 'prévisions', ou 'forecast' → 'get_forecast'. "
            "   - Sinon → 'get_current'. "
            "3. Pour 'system' : "
            "   - Si la phrase contient 'heure' → 'get_time'. "
            "   - Si la phrase contient 'CPU' ou 'mémoire' → 'get_usage'. "
            "4. Pour 'open_app' : "
            "   - Extraire le nom de l'application dans 'app_name'. "
            ""
            "EXEMPLES : "
            "1. Phrases pour 'spotify' : "
            "   - 'Joue Daft Punk' → {'intent': 'spotify', 'action': 'play_track', 'entities': {'artist': 'Daft Punk'}} "
            "   - 'Musique suivante' → {'intent': 'spotify', 'action': 'next_track', 'entities': {}} "
            "   - 'Mets le volume à 80%' → {'intent': 'spotify', 'action': 'set_volume', 'entities': {'volume': 80}} "
            "   - 'Trouve des musiques de La Fouine' → {'intent': 'spotify', 'action': 'search_track', 'entities': {'artist': 'La Fouine'}} "
            "2. Phrases pour 'weather' : "
            "   - 'Quel temps fait-il à Paris ?' → {'intent': 'weather', 'action': 'get_current', 'entities': {'city': 'Paris'}} "
            "   - 'Météo demain à Lyon' → {'intent': 'weather', 'action': 'get_forecast', 'entities': {'city': 'Lyon'}} "
            "3. Phrases pour 'system' : "
            "   - 'Quelle est l'utilisation CPU ?' → {'intent': 'system', 'action': 'get_usage', 'entities': {'resource': 'CPU'}} "
            "   - 'Éteins l'ordinateur' → {'intent': 'system', 'action': 'shutdown', 'entities': {}} "
            "4. Phrases pour 'open_app' : "
            "   - 'Ouvre Firefox' → {'intent': 'open_app', 'action': 'open', 'entities': {'app_name': 'Firefox'}} "
            "5. Phrases pour 'mistral' : "
            "   - 'Parlons de l'IA' → {'intent': 'mistral', 'action': 'conversation', 'entities': {}} "
            "6. Phrases pour 'exit' : "
            "   - 'Au revoir' → {'intent': 'exit', 'action': 'shutdown_assistant', 'entities': {}} "
            )
        },
        {"role": "user", "content": user_input}
    ]
    try:
        intent_json = call_mistral(MISTRAL_MODEL_INTENT, messages)
        print("Detected intent response:", intent_json)  # Debug
        parsed = json.loads(intent_json)

        # Vérifie que les champs obligatoires sont présents
        if "intent" not in parsed:
            parsed["intent"] = "unknown"
        if "action" not in parsed:
            parsed["action"] = "default"
        if "entities" not in parsed:
            parsed["entities"] = {}

        return parsed
    except json.JSONDecodeError:
        print("Erreur de parsing JSON, retour à unknown.")
        return {"intent": "unknown", "action": "default", "entities": {}}
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return {"intent": "unknown", "action": "default", "entities": {}}



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


