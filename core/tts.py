from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import re

def clean_text_for_tts(text):
    """
    Removes specific punctuation marks from a string for better text-to-speech.
    We'll target quotes, asterisks, and any other symbols that might cause issues.
    """
    # Regex pattern to match quotes and asterisks. You can add more characters inside the brackets.
    pattern = r'[",*`]'
    return re.sub(pattern, '', text)

def speak(text, speed=1.5):
    try:
        text = clean_text_for_tts(text)
        tts = gTTS(text=text, lang='fr')
        tts.save("temp_response.mp3")
        sound = AudioSegment.from_mp3("temp_response.mp3")
        fast_sound = sound.speedup(playback_speed=speed, chunk_size=150, crossfade=25)
        play(sound)  # lecture directe sans playsound
        os.remove("temp_response.mp3")
    except Exception as e:
        print(f"Erreur lors de la synthèse vocale : {e}")