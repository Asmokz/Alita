from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os

def speak(text):
    try:
        tts = gTTS(text=text, lang='fr')
        tts.save("temp_response.mp3")
        sound = AudioSegment.from_mp3("temp_response.mp3")
        play(sound)  # lecture directe sans playsound
        os.remove("temp_response.mp3")
    except Exception as e:
        print(f"Erreur lors de la synthèse vocale : {e}")
