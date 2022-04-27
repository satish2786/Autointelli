from celery.result import AsyncResult
from services.ITSMServices.SDP import app

def getTicketID(taskid):
  result = AsyncResult(taskid, app=app)
  while not result.ready():
    time.sleep(2)
  output, TID = result.get()
  if output:
    return TID
  else:
    return False


if __name__ == "__main__":
  output = getTicketID('49febc10-f0cb-49f3-80a0-cac5d8757b53')
  print(output)
