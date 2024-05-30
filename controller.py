import threading
import time
import random
from flask import Flask, render_template, redirect, url_for
import socket
import ast

from common import MY_ROBOT_ADDRESS, SERVER_BLE_ADDRESS

tankID = None
team = ""
qrcode = ""
affichage = ""
list_robots = []
bonuses = {}

app = Flask(__name__)

def receive():
    global list_robots
    print("Receiving thread started successfully.")
    while True:
        data = client.recv(1024)
        if not data:
            break
        message = data.decode('utf-8')
        print("received", message)
        list_robots = ast.literal_eval(message)
        print("la liste des robots est", list_robots)

def generate_bonus():
    while True:
        time.sleep(10)  # Attendre 10 secondes entre chaque bonus
        if list_robots:
            selected_robot = random.choice(list_robots)
            if selected_robot not in bonuses or not bonuses[selected_robot]:
                bonuses[selected_robot] = True  # Marquer le robot comme ayant un bonus
                send_message(f"Bonus awarded to {selected_robot}")
                print(f"Bonus awarded to {selected_robot}")

def connect_to_server():
    global client
    print("Connecting to server...")
    client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    client.connect((SERVER_BLE_ADDRESS, 4))
    print("Connected to server!")
    
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    
    bonus_thread = threading.Thread(target=generate_bonus)
    bonus_thread.start()

def send_message(message):
    client.send(message.encode('utf-8'))
    print("Message sent successfully!")

def register():
    send_message(MY_ROBOT_ADDRESS)

def send():
    try:
        while True:
            message = input("Enter message: ")
            send_message(message)
    except OSError:
        pass
    print("Disconnected")
    client.close()

@app.route("/")
def index():
    return render_template('client_ui.html', rasptank_ID=tankID, team=team, qrcode=qrcode, affichage=affichage)

@app.route("/move/<id>")
def move(id):
    try:
        print(id)
        send_message(id)
    except:
        print("Move Timeout")
    return redirect('/')

@app.route("/qr-code/")
def picture():
    try:
        print("qr scanned")
        send_message("QR code scanned")
    except:
        print("Timeout")
    return redirect('/')

if __name__ == "__main__":
    connect_to_server()
    register()  # Register with the server

    # Démarrer le thread pour envoyer des messages (juste pour test)
    send_thread = threading.Thread(target=send)
    send_thread.start()
    
    # Démarrer le serveur Flask
    app.run(host='127.0.0.1', port=5000, debug=True)