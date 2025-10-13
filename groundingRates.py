from datetime import date, datetime

#record rates in persistent storage in case of device/program shutdown

def writeRates(date, rate):
  with open("grounding.txt", "w") as f:
    f.write(str(date) + "\n")
    f.write(str(rate))
    f.close()

def readRates():
  with open("grounding.txt", "r") as f:
    lastDate = f.readline()
    rate = f.readline()
    f.close()
  lastDate = lastDate[:len(lastDate)-1]  #remove \n
  dateFormat = "%Y-%m-%d"
  lastDate = datetime.strptime(lastDate, dateFormat).date()
  return lastDate, int(rate)