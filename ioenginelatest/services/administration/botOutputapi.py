#!/usr/bin/env python

from services.utils import ConnMQ
from services.utils.aitime import getcurrentutcepoch
import time
import sys
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
import pika
from ast import literal_eval
import logging
from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS, cross_origin

bot_api = Blueprint('bot_api', __name__)

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "/var/log/autointelli/bot_output_API.log"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=104857600, backupCount=5)
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

#@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@bot_api.route('/admin/api/v2/bot/execution/output', methods=['GET', 'POST'])
def retrieve_automation_output():
  my_logger = get_logger('executeAutomation')
  my_logger.info("---------Start : API REQUEST----------")
  req = request.get_json()
  print(req)
  alert_id = int(req['alert_id'])
  countQuery='''select count(*) total from  ai_bot_executions e inner join ai_bot_executions_history eh on(e.execid=eh.fk_exec_id) where e.fk_alert_id={0}'''.format(alert_id)
  detailsQuery= '''select eh.status, eh.input, eh.output, eh.error from ai_bot_executions e inner join ai_bot_executions_history eh on(e.execid=eh.fk_exec_id) where e.fk_alert_id={0} order by eh.modifiedtime desc'''.format(alert_id)
  retCountResult = ConnPostgreSQL.returnSelectQueryResult(countQuery)
  retDetailsResult = ConnPostgreSQL.returnSelectQueryResult(detailsQuery)
  botOutput = []
  if retCountResult["result"] == "success":
      total_Bots = retCountResult['data'][0]['total']
  if retDetailsResult["result"] == "success":
    for output in retDetailsResult['data']:
      botOutput.append({'status': output['status'], 'name': output['input']['name'], 'order': output['input']['order'], 'output': output['output'], 'error': output['error']})
    return jsonify({'result': 'success', 'total': total_Bots, 'bot_flow': botOutput})
  else:
    my_logger.error("---------END : API REQUEST : No Data Found")
    return jsonify({'result': 'failure', 'message': 'No Data Found'})
