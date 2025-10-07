import wave
import os
from piper import PiperVoice, SynthesisConfig

syn_config = SynthesisConfig(
    speaker_id=1
)

voice = PiperVoice.load("models/en_GB-semaine-medium.onnx")
def tts(text):
    with wave.open("test.wav", "wb") as wav_file:
        voice.synthesize_wav(text, wav_file, syn_config=syn_config)
        
    os.system("aplay test.wav")