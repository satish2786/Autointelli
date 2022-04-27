import datetime

def getcurrentutcepoch():
  utcepoch = int((datetime.datetime.utcnow() - datetime.datetime(1970,1,1)).total_seconds())
  return(utcepoch)
