import os
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import speech_recognition as sr
import pyaudio
import psutil

load_dotenv()

picokey = os.getenv("PICOKEY")
porcupine = pvporcupine.create(
  access_key=picokey,
  keywords=["picovoice"]
)

recorder = PvRecorder(device_index=1, frame_length=porcupine.frame_length)
recorder.start()

def testCommand():
  print("Listening...")
  print("Done")

def processAudio():
  pcm = recorder.read()
  return porcupine.process(pcm)

def closeRecorder():
  recorder.stop()
  recorder.delete()
  porcupine.delete()

def speechToText():
  recognizer = sr.Recognizer()
  with sr.Microphone() as source:
    audio = recognizer.listen(source)
    try:
      text = recognizer.recognize_google(audio, language="en-US")
      print(f"You said: {text}")
    except:
      print("Please try again")

def get_ram_usage():
  """Returns the current RAM usage of the process in MiB."""
  process = psutil.Process(os.getpid())
  mem_info = process.memory_info()
  return mem_info.rss / 1024 ** 2 # Convert bytes to MiB

if __name__ == "__main__":
  while True:
    detectWake = processAudio()
    if detectWake != -1:
      recorder.stop()
      print("Listening...")
      speechToText()
      recorder.start()
      print("Prompt Ended")
