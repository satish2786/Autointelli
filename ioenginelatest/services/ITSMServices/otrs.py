from pyotrs import Ticket, Article, Client
import json

Instance="http://95.216.28.228:3890"
User="pocuser"
Pass="@ut0!ntell!@123"

def CreateTicket(Subject, Body, group):
  try:
    CustomerUser = 'democustomer'
    Title = Subject
    State = 'open'
    Priority = '3 normal'
    if group == 'automation':
      Queue = 'Incidents'
    else:
      Queue = 'Service Requests'
    client = Client(Instance, User, Pass)
    client.session_create()
    new_ticket = Ticket.create_basic(Title=Title, Queue=Queue, State=State, Priority=Priority, CustomerUser=CustomerUser)
    first_article = Article({"Subject": Subject, "Body": Body})
    result = client.ticket_create(new_ticket, first_article)
    TNO = result['TicketNumber']
    TID = result['TicketID']
    return json.dumps({"TID": TNO, "REFID": TID, "Status": True})
  except Exception as e:
    return json.dumps({"Message": "Error Creating Ticket"+str(e), "Status": False})


def UpdateState(TID, ticketstate):
  try:
    client = Client(Instance, User, Pass)
    client.session_create()
    update = client.ticket_update(TID, State=ticketstate)
    return ({"Message": "Status changed to In Progress", "Status": True})
  except Exception as e:
    return ({"Message": str(e), "Status": False})


def UpdateQueue(TID,TicketQueue):
  try:
    client = Client(Instance, User, Pass)
    client.session_create()
    update = client.ticket_update(TID, Queue=TicketQueue)
    return True
  except Exception as e:
    print(str(e))
    return False


def AddWorklog(TID,Notes):
  try:
    client = Client(Instance, User, Pass)
    client.session_create()
    my_article = Article({"Subject": "Ticket Update from Autointelli", "Body": Notes})
    update = client.ticket_update(TID, article=my_article)
    return ({"Message": "Worklog added", "Status": True})
  except Exception as e:
    return ({"Message": "Error" + str(e), "Status": False})


if __name__ == "__main__":
  TNO= CreateTicket("TEST","TEST", "automation")
  print(TNO)
