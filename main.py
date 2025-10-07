import os
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import speech_recognition as sr
import pyaudio
import psutil
from geminiFunctions import geminiChatRequest

load_dotenv()

picokey = os.getenv("PICO_KEY")
porcupine = pvporcupine.create(
  access_key=picokey,
  keywords=["picovoice"]
)

recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
recorder.start()

def processAudio():
  """
  Use the initialized PvRecorder to process the current audio window to detect the porcupine wake word
  Returns:
    processResult (int): the index of the detected porcupine keyword or -1 if none were detected
  """
  pcm = recorder.read()
  return porcupine.process(pcm)

def closeRecorder():
  """Stops the initiallized PvRecorder from recording audio and releases any resources used by the Pvrecorder"""
  recorder.stop()
  recorder.delete()
  porcupine.delete()


def speechToText():
  """
  Take in speech from the user's default mic and convert it to text
  Returns:
    text (str): User's speech converted to a text str or None on error
  """
  recognizer = sr.Recognizer()
  with sr.Microphone() as source:
    audio = recognizer.listen(source)
    try:
      text = recognizer.recognize_google(audio, language="en-US")
      print(f"You said: {str(text)}")
      return str(text)
    except Exception as e:
      print(e)
      print("Please try again")
      return None

def get_ram_usage():
  """Returns the current RAM usage of the process in MiB"""
  process = psutil.Process(os.getpid())
  mem_info = process.memory_info()
  return mem_info.rss / 1024 ** 2 # Convert bytes to MiB

if __name__ == "__main__":
  geminiChat = None
  while True:
    detectWake = processAudio()
    if detectWake != -1:
      recorder.stop()
      print("Listening...")
      userPrompt = speechToText()
      if userPrompt == None:
        # alert user
        print("\nError has occured")
        print("Prompt Ended")
        recorder.start()
        continue
      if userPrompt == "reset chat":
        geminiChat = None
        print("\nChat Reset")
        print("Prompt Ended")
        recorder.start()
        continue

      geminiResponse, geminiChat = geminiChatRequest(
          prompt=userPrompt,
          chat=geminiChat,
          model="gemini-2.5-flash"
        )      
      if geminiResponse == None:
        print("Error has occured")
        
      print("Prompt Ended")
      recorder.start()