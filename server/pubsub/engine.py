from flask import Blueprint
from flask_sockets import Sockets

from common.auth import authenticate

ws = Blueprint('ws', __name__)

@ws.route('/sync')
def sync_channel(socket):
    while not socket.closed:
        message = socket.receive()
        socket.send(message)
