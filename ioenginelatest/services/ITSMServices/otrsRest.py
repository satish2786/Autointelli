#!/usr/bin/env python
import sys
import logging
from flask import Flask, jsonify, request
from logging.handlers import TimedRotatingFileHandler
from otrs import CreateTicket

app = Flask(__name__)

@app.route('/otrs/6/create', methods=['POST'])
def create_ticket():
  try:
    app.logger.info("Received Request: OK")
    RequestID = "xxxx-Ticket-Create-xxxx"
    data = request.get_json()
    app.logger.info(str(data))
    if data['Title'] == '' or data['Queue'] == '' or data['State'] == '' or data['Priority'] == '' or data['CustomerUser'] == '' or data['Subject'] == '' or data['Body'] == '':
      return jsonify({"ERROR": "Invalid Arguments Detected", "Status": "Rejected"})
    app.logger.info("Data Received for OTRS Ticket Create")
    app.logger.info("Creating OTRS Ticket")
    result = CreateTicket(data['Title'], data['Queue'], data['State'], data['Priority'], data['CustomerUser'], data['Subject'], data['Body'])
    return jsonify({"JOBID": RequestID, "Status": "Success", "TicketNumber": result})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Rejected"})

if __name__ == '__main__':
    try:
      formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
      handler = TimedRotatingFileHandler('logs/OTRS.log', when='midnight', interval=1)
      handler.setLevel(logging.DEBUG)
      handler.setFormatter(formatter)
      app.logger.addHandler(handler)
      app.logger.setLevel(logging.DEBUG)
      app.run(host='0.0.0.0', port=5005, debug=False)
    except Exception as e:
      print("Exception occured : "+str(e))
      sys.exit()
