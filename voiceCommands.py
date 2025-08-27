import os
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import speech_recognition as sr
import pyaudio

load_dotenv()

picokey = os.getenv("PICOKEY")
porcupine = pvporcupine.create(
  access_key=picokey,
  keyword_paths=["HeyChatPal.ppn"]
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


if __name__ == "__main__":
  while True:
    detectWake = processAudio()
    if detectWake != -1:
      recorder.stop()
      print("Listening...")
      speechToText()
      recorder.start()
      print("Prompt Ended")
