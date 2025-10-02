import pvporcupine
import pyaudio
import struct
import os
from dotenv import load_dotenv

load_dotenv()

# Remplacez par votre chemin vers le modèle Porcupine pour le français
# Vous pouvez trouver le modèle ici : https://github.com/Picovoice/porcupine/tree/master/resources/keyword_files/fr
cwd = os.getcwd()
KEYWORD_FILE_PATH = os.path.join(cwd, "Alita_fr_linux_v3_0_0.ppn")
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
MODEL_PATH = os.path.join(cwd, "porcupine_params_fr.pv")

def listen_for_wake_word(keyword_path, model_path, access_key):
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path],
            model_path=model_path  # Ajout de ce paramètre
        )
    except Exception as e:
        print(f"Erreur lors de la création de l'instance Porcupine : {e}")
        return False

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length)

    print("🤖 En attente du mot de réveil 'Alita'...")
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        result = porcupine.process(pcm)

        if result >= 0:
            print("🔊 Mot de réveil 'Alita' détecté ! Je vous écoute...")
            return True

    porcupine.delete()
    audio_stream.close()
    pa.terminate()