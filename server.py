from flask import Flask, request, jsonify
import threading
from bluetooth import *

app = Flask(__name__)

participants = []
robots = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    mac_address = data['mac_address']
    if mac_address not in participants:
        participants.append(mac_address)
        return jsonify({"status": "registered", "participants": participants}), 200
    else:
        return jsonify({"status": "already registered"}), 400

@app.route('/start', methods=['POST'])
def start_race():
    return jsonify({"status": "Race started"}), 200

@app.route('/command/<mac_address>', methods=['POST'])
def send_command(mac_address):
    command = request.json['command']
    if mac_address in robots:
        robot_service_url = robots[mac_address]
        response = requests.post(f"http://{robot_service_url}/execute", json={'command': command})
        return jsonify({"status": "Command sent", "response": response.json()}), 200
    else:
        return jsonify({"error": "Robot not found"}), 404

def handle_robot_connection():
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    advertise_service(server_sock, "RobotServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE])

    print(f"Waiting for connection on RFCOMM channel {port}")

    while True:
        client_sock, client_info = server_sock.accept()
        mac_address = client_sock.recv(1024).decode('utf-8')
        robots[mac_address] = client_info[0]
        print(f"Robot {mac_address} connected from {client_info}")

if __name__ == '__main__':
    threading.Thread(target=handle_robot_connection).start()
    app.run(host='0.0.0.0', port=5000)
