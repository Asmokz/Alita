import pyaudio
import numpy as np
import time
import whisper
import torch

model = whisper.load_model("medium")

def record_and_transcribe():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)

    print("🎙️ Enregistrement démarré...")
    frames = []
    silent_frames_count = 0
    max_silent_frames = 16000 * 2 / 1024  # Environ 2 secondes de silence

    #if torch.cuda.is_available():
    #    print("✅ GPU (CUDA) est disponible et sera utilisé.")
    #    print(f"Nom du GPU : {torch.cuda.get_device_name(0)}")
    #else:
    #    print("❌ GPU (CUDA) n'est pas disponible. Whisper utilisera le CPU.")

    while True:
        data = stream.read(1024)
        frames.append(data)
        
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Calcule le niveau d'énergie moyen du morceau audio
        rms = np.sqrt(np.mean(np.square(audio_data)))

        if rms < 45:  # Le seuil de silence peut être ajusté
            silent_frames_count += 1
        else:
            silent_frames_count = 0

        if silent_frames_count > max_silent_frames:
            break

    print("⏹️ Enregistrement arrêté.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_bytes = b''.join(frames)
    audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    if audio.size == 0:
        print("⚠️ Aucun audio capturé.")
        return ""

    print("🧠 Transcription en cours...")
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(language="fr")
    result = whisper.decode(model, mel, options)

    return result.text