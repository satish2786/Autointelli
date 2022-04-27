#!/usr/bin/env python
from threading import Lock
from flask import Flask,  session, request, jsonify
from flask_socketio import SocketIO, emit

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


@app.route('/admin/api/v2/notifications/async', methods=['POST', 'GET'])
def emit_event():
  data = request.get_json()
  print(data)
  Module = data['Module']
  infoType = data['informationType']
  Data = data['Data']
  socketio.emit('my_response', {'Module': Module, 'Type': infoType, 'Data': Data },  namespace='/test')
  return jsonify({"Message": "Success"})



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000, debug=True)
