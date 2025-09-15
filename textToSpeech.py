import pyttsx3

# integrate this into voiceCommands.py

engine = pyttsx3.init()

# RATE
rate = engine.getProperty('rate')   # getting details of current speaking rate
# VOLUME
volume = engine.getProperty('volume')   # getting to know current volume level (min=0 and max=1)

voices = engine.getProperty('voices')       # getting details of current voices
engine.setProperty('voice', voices[0].id)   # changing index, changes voices. 0 for male, 1 for female

engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()