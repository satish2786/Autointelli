import psycopg2
from services.utils.decoder import decode, encode
from flask import request,jsonify, Blueprint
import json
import requests
import os

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

proc_api = Blueprint('proc_api', __name__)


@proc_api.route("/admin/api/v2/automation/process/instances/<container>/<procid>", methods = ['GET'])
def get_ProcessImage(container=None, procid=None):
  try:
    SERVER = "10.10.25.91"
    PORT = 8085
    URL = "http://{0}:{1}/kie-server/services/rest/server/containers/{2}/images/processes/instances/{3}".format(SERVER,PORT,container, procid)
    print(URL)
    output = requests.get(URL, auth=("kieserver", "kieserver1!"))
    if output.status_code == 200:
      image_data = output.text
      filename  = """{0}_{1}.svg""".format(container,procid)
      FH = open('/usr/share/nginx/html/downloads/{0}'.format(filename),'w')
      FH.write(image_data)
      FH.close()
      return jsonify({"data":"http://10.10.25.91/downloads/{1}".format(SERVER,filename),"result" : "success"})
    else:
      return jsonify({"message":"No Process Image found","result" : "failure"})
  except Exception as e:
    return jsonify({"message":"Error in output","result" : "failure : "+str(e)})



@proc_api.route("/admin/api/v2/automation/process/images/<container>/<procid>", methods = ['GET'])
def get_ProcessImage_default(container=None, procid=None):
  try:
    SERVER = "10.10.25.91"
    PORT = 8085
    URL = "http://{0}:{1}/kie-server/services/rest/server/containers/{2}/images/processes/{3}".format(SERVER,PORT,container, procid)
    print(URL)
    output = requests.get(URL, auth=("kieserver", "kieserver1!"))
    if output.status_code == 200:
      image_data = output.text
      filename  = """{0}_proc_image.svg""".format(container)
      FH = open('/usr/share/nginx/html/downloads/{0}'.format(filename),'w')
      FH.write(image_data)
      FH.close()
      return jsonify({"data":"http://10.10.25.91/downloads/{1}".format(SERVER,filename),"result" : "success"})
    else:
      return jsonify({"message":"No Process Image found","result" : "failure"})
  except Exception as e:
    return jsonify({"message":"Error in output","result" : "failure : "+str(e)})


