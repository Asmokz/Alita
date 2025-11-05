import requests


def send_to_n8n(intent_data: dict):
    """Envoie les données d'intent à n8n et retourne la réponse."""
    url = "http://127.0.0.1:5678/webhook-test/alita"  # URL de ton webhook n8n
    try:
        response = requests.post(url, json=intent_data, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", "OK")
        else:
            return f"Erreur n8n : {response.status_code}"
    except Exception as e:
        return f"Erreur réseau : {str(e)}"
