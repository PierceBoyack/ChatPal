import pyttsx3
from phonemizer import phonemize

# integrate this into voiceCommands.py

engine = pyttsx3.init(driverName="sapi5")

# RATE
# rate = engine.getProperty('rate')   # getting details of current speaking rate
# VOLUME
volume = engine.getProperty('volume')   # getting to know current volume level (min=0 and max=1)

voices = engine.getProperty('voices')      # getting details of current voices
print(voices)
engine.setProperty('voice', voices[0].id)   # changing index, changes voices. 0 for male, 1 for female

def tts(text: str):
  """
  Play a tts message using 
  """
  phonemes = phonemize(text)
  engine.say(phonemes)
  engine.runAndWait()
  engine.stop()

tts("I like apple pie")