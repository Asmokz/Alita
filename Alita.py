import language_tool_python
import sounddevice as sd
import numpy as np
import keyboard
import whisper
import time
from core.record import record_and_transcribe
from core.detect import listen_for_wake_word, MODEL_PATH, ACCESS_KEY, KEYWORD_FILE_PATH
from functions.weather import get_weather
from functions.mistral import ask_mistral
from core.tts import speak

# ... (votre code AudioRecorder et record_and_transcribe) ...

def main_loop():
    print("🤖 Assistant personnel en attente...")
    while True:
        # Attendre la détection du mot de réveil
        if listen_for_wake_word(KEYWORD_FILE_PATH, MODEL_PATH, ACCESS_KEY):
            transcription = record_and_transcribe()
            if transcription and transcription.strip():
                print(f"🗣️ Vous avez dit : {transcription}")
                process_command(transcription)

def process_command(command):
    command = command.lower()
    if "météo" in command:
        print("Météo demandée.")
        words = command.split()
        try:
            # On trouve l'index du mot "météo"
            index_of_weather = words.index("météo")
            # On prend le mot qui suit directement "météo"
            city = words[index_of_weather + 1]
            
            # 4. Appeler la fonction météo avec la ville trouvée
            weather_info = get_weather(city.capitalize())
            print(weather_info)
            speak(weather_info)
        except (ValueError, IndexError):
            # En cas d'erreur (pas de mot "météo" ou pas de mot après)
            print("Veuillez spécifier une ville après le mot 'météo'. Par exemple : 'météo Paris'.")
            speak("Veuillez spécifier une ville après le mot météo.")
    elif "mistral" in command:
        print("Requête pour Mistral.ai...")
        
        # Sépare la commande après le mot "mistral"
        parts = command.split("mistral", 1)
        if len(parts) > 1 and parts[1].strip():
            user_input_for_mistral = parts[1].strip()
            print(user_input_for_mistral)
            # Appel à la fonction qui interroge l'API de Mistral
            try:
                mistral_response = ask_mistral(user_input_for_mistral)
                print("Réponse de Mistral :", mistral_response)
                speak(mistral_response)
            except Exception as e:
                print(f"Erreur lors de l'appel à Mistral : {e}")
                speak("Désolé, une erreur est survenue lors de la communication avec le service Mistral.")
        else:
            print("Veuillez poser une question après le mot 'mistral'.")
            print("Veuillez poser une question après le mot 'mistral'") 
    elif "bonjour" in command:
        print("Bonjour ! Comment puis-je vous aider ?")
        speak("Bonjour ! Comment puis-je vous aider ?")
    elif "heure" in command:
        # Code pour obtenir et annoncer l'heure
        heure = time.strftime("%H:%M")
        print(f"Il est actuellement {heure}.")
        speak(f"Il est actuellement {heure}.")
    elif "quitter" in command:
        print("Au revoir !")
        speak("Au revoir !")
        exit()
    else:
        print("Désolé, je n'ai pas compris la commande.")
        speak("Désolé, je n'ai pas compris la commande.")

if __name__ == "__main__":
    main_loop()