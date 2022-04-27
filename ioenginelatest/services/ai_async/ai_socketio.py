from flask import Flask, render_template, request,  jsonify
from flask_socketio import SocketIO, emit
import json
from threading import Lock
from services.utils.ConnMQ import send2MQ
from engineio.async_drivers import gevent


async_mode = 'gevent'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)
thread = None
thread_lock = Lock()

@socketio.on('my event', namespace='/autointelli_async')
def autointelli_async_message(message):
    print(message['data'])
    emit('my response', {'data': message['data']})

@socketio.on('initiatediscovery', namespace='/autointelli_async')
def autointelli_async_message(message):
    print(message)
    send2MQ('discovery_socket','automation', 'discovery_socket',json.dumps(message))

@socketio.on('connect', namespace='/autointelli_async')
def autointelli_async_connect():
    print("Client Connected")
    emit('my response', {'data': 'Connected To Backend'})

@socketio.on('disconnect', namespace='/autointelli_async')
def autointelli_async_disconnect():
    print('Client disconnected')


@app.route('/admin/api/v2/notifications/async', methods=['POST', 'GET'])
def emit_event():
  try:
    data = request.get_json()
    Module = data['Module']
    infoType = data['InformationType']
    Data = data['Data']
    Action = data['Action']
    if Module == "alert":
      socketio.emit('alert', {'Module': Module, 'Type': infoType, 'Action': Action, 'Data': Data },  namespace='/autointelli_async')
    else:
      socketio.emit('discovery_result', {'Module': Module, 'Type': infoType, 'Action': Action, 'Data': Data },  namespace='/autointelli_async')
    return jsonify({"Message": "Success"})
  except Exception as e:
    return jsonify({"Message": "Failure "+str(e)})
    

if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=3891)

