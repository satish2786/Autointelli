import json
from services.utils.decoder import decode, encode
from flask import Blueprint, jsonify, request

patchadmin_api = Blueprint('patchadmin_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])


@patchadmin_api.route('/admin/api/v2/patchmodule/insert', methods=['POST'])
def insert_plan_details():
  """
  {
    "name": "Plan A",
    "servergroup": [
      "WebServer",
      "TerminalServers",
      "DBServers"
    ],
    "updates": [
      "Application",
      "Connectors",
      "Critical Updates"
    ],
    "blacklist": [
      "KB12345677"
    ],
    "whitelistlist": [
      "KB123456377"
    ],
    "Reboot": {
      "Reboot": "Yes",
      "Timeout": 1200
    }
  }
  """
  try:
    data = request.get_json()
    print(data)
    return jsonify({'Status': 'Success', 'Message': "Plan Created Successfully"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@patchadmin_api.route('/admin/api/v2/patchmodule/getdetails', methods=['GET'])
def get_plan_details():
  try:
    data = {
  'Plan A': {
  'servergroup': [
    'WebServer',
    'TerminalServers',
    'DBServers'
  ],
  'updates': [
    'Application',
    'Connectors',
    'Critical Updates'
  ],
  'blacklist': [
    'KB12345677'
  ],
  'whitelistlist': [
    'KB123456377'
  ],
  'Reboot': {
    'Reboot': 'Yes',
    'Timeout': 1200
  }
 },
 'Plan B': {
  'servergroup': [
    'WebServer',
    'TerminalServers',
    'DBServers'
  ],
  'updates': [
    'Application',
    'Connectors',
    'Critical Updates'
  ],
  'blacklist': [
    'KB12345677'
  ],
  'whitelistlist': [
    'KB123456377'
  ],
  'Reboot': {
    'Reboot': 'Yes',
    'Timeout': 1200
  }
 }
}
    return jsonify({'Status': 'Success', 'Data': data})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@patchadmin_api.route('/admin/api/v2/patchmodule/deletedetails', methods=['DELETE'])
def delete_plan_details():
  try:
    """{"name": "Plan A"}"""
    return jsonify({'Status': 'Success', 'Message': 'Plan Deleted Successfully'})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@patchadmin_api.route('/admin/api/v2/patchmodule/editdetails', methods=['POST'])
def edit_plan_details():
  try:
    data = {
  'Plan A': {
  'servergroup': [
    'WebServer',
    'TerminalServers',
    'DBServers'
  ],
  'updates': [
    'Application',
    'Connectors',
    'Critical Updates'
  ],
  'blacklist': [
    'KB12345677'
  ],
  'whitelistlist': [
    'KB123456377'
  ],
  'Reboot': {
    'Reboot': 'Yes',
    'Timeout': 1200
  }
 }
}
    return jsonify({'Status': 'Success', 'Message': 'Plan Updated Successfully'})
  except Exception as e:
    return jsonify({"Status": "Failure", "Message": str(e)})


@patchadmin_api.route('/admin/api/v2/patchmodule/executeplan', methods=['POST'])
def execute_plan_details():
  try:
    data = request.get_json()
    return jsonify({'Status': 'Success', 'Message': 'Execution initiated, Check Results once available'})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})

@patchadmin_api.route('/admin/api/v2/patchmodule/masters', methods=['GET'])
def master_data():
  try:
    data = {
    'UpdateSelection': [
    'Application',
    'Connectors',
    'Critical Updates',
    'Definition Update',
    'Developer Kits',
    'Feature Packs',
    'Guidance',
    'Security Updates',
    'Service Packs',
    'Tools',
    'Update Rollups',
    'Updates'
      ]
    }
    return jsonify({'Status': 'Success', 'Data': data})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})
