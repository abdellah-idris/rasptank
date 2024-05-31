from flask import Flask, render_template, redirect, url_for
import socket
import uuid
import requests
import re

from common import MY_ROBOT_ADDRESS, SERVER_BLE_ADDRESS

tankID = None
team = ""
qrcode = ""
affichage = ""

app = Flask(__name__)


def connect_to_server():
    print("Connecting to server...")
    client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    client.connect((SERVER_BLE_ADDRESS, 4))
    print("Connected to server!")
    return client


# socket
client = connect_to_server()


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

    except :
        print("Timeout")

    return redirect('/')


# run  the app
if __name__ == "__main__":
    register()  # register with the server
    send()  # just for test
    app.run(host='127.0.0.1', port=5000, debug=True)