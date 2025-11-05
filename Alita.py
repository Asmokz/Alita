# Alita.py
import language_tool_python
import sounddevice as sd
import numpy as np
import keyboard
import whisper
import time
import threading
import sys
from core.n8n import send_to_n8n
from core.record import record_and_transcribe
from core.detect import listen_for_wake_word, MODEL_PATH, ACCESS_KEY, KEYWORD_FILE_PATH
from functions.weather import get_weather
from functions.mistral import ask_mistral, detect_intent_and_entities
from functions.system_monitor import get_system_status
from core.tts import speak
from functions.loadApp import open_app, load_app_mapping
from gui import AlitaGUI # Import the GUI class
from functions.spotify import SpotifyController
spc = SpotifyController()
import logging


class AlitaAssistant:
    def __init__(self):
        # Initialize GUI and make it available to the rest of the application
        self.gui = AlitaGUI(self)
        self.app_mapping = load_app_mapping()
        # Initialize a lock to prevent race conditions when updating the GUI
        self.gui_lock = threading.Lock()
        self.should_exit = False  # Drapeau pour contrôler la boucle principale
        self.logger = self.setup_logger()
    
        # --- CONFIGURATION LOGGER ---
    def setup_logger(self):
        logger = logging.getLogger("AlitaLogger")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler("alita.log", encoding="utf-8")
        file_handler.setFormatter(formatter)

        if not logger.hasHandlers():
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

    def main_loop(self):
        self.gui.update_state("initial", "🤖 Assistant personnel en attente...")
        while not self.should_exit:
            # Attendre la détection du mot de réveil
            self.gui.update_state("initial", "🤖 En attente du mot de réveil 'Alita'...")
            if listen_for_wake_word(KEYWORD_FILE_PATH, MODEL_PATH, ACCESS_KEY):
                self.gui.update_state("listening", "🔊 Mot de réveil 'Alita' détecté ! Je vous écoute...")
                
                transcription = record_and_transcribe()
                
                if transcription and transcription.strip():
                    self.gui.update_state("processing", f"🗣️ Vous avez dit : {transcription}")
                    self.process_command(transcription)

    



    def process_command(self, command):
        """
        Traite une commande en détectant l'intention puis en appelant
        la fonction correspondante (météo, système, Spotify, apps, conversation).
        """
        command = command.lower()
        self.logger.info(f"Commande reçue: {command}")

        # --- Détecter l'intention avec Mistral ---
        try:
            result = detect_intent_and_entities(command)
            intent = result["intent"]
            entities = result.get("entities", {})
            self.logger.debug(f"Intent détecté: {intent} avec entités: {entities}")
        except Exception as e:
            self.gui.update_state("speaking", f"Erreur lors de la détection d'intention : {e}")
            self.logger.warning(f"Intent '{intent}' non reconnu → fallback sur conversation")
            speak("Désolé, je n'ai pas pu analyser votre commande.")
            return

        # --- Dispatcher selon l'intention ---
        if intent == "weather":
            try:
                city = entities.get("city")
                weather_info = get_weather(city.capitalize())
                self.gui.update_state("speaking", weather_info)
                speak(weather_info)
            except (ValueError, IndexError):
                self.gui.update_state("speaking", "Veuillez spécifier une ville après le mot météo.")
                speak("Veuillez spécifier une ville après le mot météo.")

        elif intent == "system":
            stats_info = get_system_status()
            self.gui.update_state("speaking", stats_info)
            speak(stats_info)

        elif intent == "mistral":
            try:
                reply = ask_mistral(command)  # Appel au modèle conversationnel
                self.gui.update_state("speaking", reply)
                speak(reply)
            except Exception as e:
                self.gui.update_state("speaking", "Désolé, une erreur est survenue lors de la conversation.")
                speak("Désolé, une erreur est survenue lors de la conversation.")

        elif intent == "open_app":
            # Recherche d'applications/bundles comme dans ton code original
            try:
                command_name = next(cmd for cmd in self.app_mapping if cmd.replace("bundle:", "") in command)
                target = self.app_mapping[command_name]

                if isinstance(target, list):
                    self.gui.update_state("speaking", f"Je lance le bundle {command_name.replace('bundle:', '')}.")
                    speak(f"Je lance le bundle {command_name.replace('bundle:', '')}.")
                    for app in target:
                        if app in self.app_mapping:
                            open_app(self.app_mapping[app])
                        else:
                            self.gui.update_state("speaking", f"⚠️ Je ne connais pas l'application {app} dans ce bundle.")
                            speak(f"Je ne connais pas l'application {app} dans ce bundle.")
                else:
                    open_app(target)
                    self.gui.update_state("speaking", f"J'ouvre {command_name}.")
                    speak(f"J'ouvre {command_name}.")
            except StopIteration:
                self.gui.update_state("speaking", "Je ne connais pas cette application.")
                speak("Je ne connais pas cette application.")
            except Exception as e:
                self.gui.update_state("speaking", f"Erreur lors de l'ouverture de l'application : {e}")
                speak(f"Erreur lors de l'ouverture de l'application : {e}")

        elif intent == "spotify":
            # Envoi à n8n
            n8n_response = send_to_n8n(result)
            print("Réponse de n8n :", n8n_response)

            self.gui.update_state("speaking", n8n_response)
            speak(n8n_response)

        elif intent == "time":
            heure = time.strftime("%H:%M")
            self.gui.update_state("speaking", f"Il est actuellement {heure}.")
            speak(f"Il est actuellement {heure}.")

        elif intent == "greeting":
            self.gui.update_state("speaking", "Bonjour ! Comment puis-je vous aider ?")
            speak("Bonjour ! Comment puis-je vous aider ?")

        elif intent == "exit":
            self.gui.update_state("speaking", "Au revoir !")
            speak("Au revoir !")
            self.should_exit = True
            self.gui.root.quit()
            self.gui.root.destroy()

        else:
            self.gui.update_state("speaking", "Désolé, je n'ai pas compris la commande.")
            speak("Désolé, je n'ai pas compris la commande.")

    def run(self):
        # Start the assistant's main loop in a separate thread
        assistant_thread = threading.Thread(target=self.main_loop)
        assistant_thread.daemon = True
        assistant_thread.start()
        
        # Start the GUI's main loop in the main thread
        self.gui.root.mainloop()

if __name__ == "__main__":
    app = AlitaAssistant()
    app.run()