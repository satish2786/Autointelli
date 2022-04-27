#!/usr/bin/env python
import sys
import optparse
import requests 
import json
import datetime
import time

__VERSION__ = '1.0.0'


def parse_args():
    now = datetime.datetime.now()
    date_time = now.strftime("%d-%m-%Y %H:%M:%S")
    
    version = 'send2autointelli.py, Version %s' % __VERSION__

    parser = optparse.OptionParser()
    parser.add_option("-T", "--type", type="str", help="Request Type ( http / https )")
    parser.add_option("-H", "--hostname", help="The Autointelli hostname to be connected to.")
    parser.add_option("-P", "--port", default=8000, type="int",
                      help="Port to use to connect to the client.")
    parser.add_option("-p", "--priority", default="Medium", type="str",
                      help="Alert Priority")
    parser.add_option("-t", "--time", default=date_time, type="str",
                      help="Alert Created Time in DD-MM-YYYY HH:MM:SS, If no option"
                           " is provided, defaults to current time")
    parser.add_option("-m", "--machine", type="str",
                      help="The CI or the System that is affected")
    parser.add_option("-a", "--application", type="str",
                      help="The Application that is affected")
    parser.add_option("-c", "--component", default="Service Down",
                      help="Optional, Alert Component, E.g: Disk, Memory, Service")
    parser.add_option("-v", "--value", default=1,
                      help="Optional, The Value of the component affected")
    parser.add_option("-d", "--description", type="str",
                      help="Summary Of the Alert")
    parser.add_option("-n", "--notes", type="str",
                      help="detailed description of the alert")
    parser.add_option("-s", "--severity", type="str",
                      help="Severity of the Alert E.g OK, WARNING, CRITICAL, UNKNOWN")
    parser.add_option("-S", "--source", default="autointelli", type="str",
                      help='Source of the Alert')
    parser.add_option("-C", "--customer", default="Anonymous", type="str",
                      help='Optional, Customer ID')
    parser.add_option("-J", "--json", type="str",
                      help='JSON Format of Data')
    parser.add_option("-V", "--version", action='store_true',
                      help='Print version number of plugin.')
    parser.add_option("-D", "--debug", action='store_true',
                      help='Optional, Debug')
    options, _ = parser.parse_args()

    if options.version:
        print(version)
        sys.exit(0)

    if options.json:
        pass

    elif not options.type:
        parser.print_help()
        parser.error("Request Type is required, use --type http or https")

    elif not options.hostname:
        parser.print_help()
        parser.error("Autointelli IP / Hostname is required for use.")

    elif not options.machine:
        parser.print_help()
        parser.error('machine is required, use --machine')

    elif not options.time:
        parser.print_help()
        parser.error('time is required, use --time')

    elif not options.application:
        parser.print_help()
        parser.error('application is required, use --application')

    elif not options.description:
        parser.print_help()
        parser.error('description is required, use --description')

    elif not options.notes:
        parser.print_help()
        parser.error('notes is required, use --notes')
   
    elif not options.source:
        parser.print_help()
        parser.error('source is required, use --source')
      
    elif not options.severity:
        parser.print_help()
        parser.error('severity is required, use --severity')

    return options


def main():
  try:
    options = parse_args()
    TYPE        = options.type
    HOSTNAME    = options.hostname
    PORT        = options.port
    MACHINE     = options.machine
    APPLICATION = options.application
    DESCRIPTION = options.description
    NOTES       = options.notes
    SEVERITY    = options.severity
    TIME        = options.time
    SOURCE      = options.source
    #OPTIONAL
    JSON        = options.json
    PRIORITY    = options.priority
    COMPONENT   = options.component
    VALUE       = options.value
    CUSTOMER    = options.customer
    EVENT_TIME  = int(time.time()) 
 
    #PRINT
    if options.debug and options.json:
      print("---------------ARGUMENTS---------------")
      print(JSON)
      print("---------------ARGUMENTS---------------")
    if options.debug and not options.json:
      print("---------------ARGUMENTS---------------")
      print(TYPE) 
      print(HOSTNAME) 
      print(PORT) 
      print(MACHINE) 
      print(APPLICATION) 
      print(DESCRIPTION) 
      print(NOTES) 
      print(SEVERITY) 
      print(TIME) 
      print(SOURCE) 
      print(PRIORITY) 
      print(COMPONENT) 
      print(VALUE) 
      print(CUSTOMER) 
      print(EVENT_TIME)
      print("---------------ARGUMENTS---------------")
 
    #FORM URL 
    URL = "{0}://{1}:{2}/evm/api1.0/endpoints/eventreceiver".format(TYPE,HOSTNAME,PORT)
    HEADERS = {'Content-Type': 'application/json'}
    if JSON:
      PAYLOAD = json.loads(JSON)
    else:
      PAYLOAD = {'priority': PRIORITY, 'msg_updated_time': TIME, 'machine': MACHINE, 'application': APPLICATION, 'value': str(VALUE), 'cmdline': COMPONENT, 'description': DESCRIPTION, 'extra_description': NOTES, 'severity': SEVERITY, 'source': SOURCE, 'event_created_time': EVENT_TIME, 'customer_id': CUSTOMER}
    if options.debug:
      print("--------------URL DETAILS---------------")
      print(URL)
      print(HEADERS)
      print(PAYLOAD)
      print("--------------URL DETAILS---------------")
    output = requests.post(URL, headers=HEADERS, data=json.dumps(PAYLOAD))
    if output.status_code == 200:
      print(output.text)
    else:
      print("Error in Request")
      print(output.text)

  except Exception as e:
    print(str(e)) 

if __name__ == "__main__":
    main()
