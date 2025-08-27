import os
from dotenv import load_dotenv

load_dotenv()

picokey = os.getenv("PICOKEY")

def testCommand():
  print("Listening...")
  print("Done")


