from flask import Flask, render_template, redirect, url_for
import socket
import uuid
import requests
import re


tankID = None
team = ""
qrcode = ""
affichage = ""

app = Flask(__name__)


def get_mac_address():
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    print ("my mac: " + mac)

    return mac


def connect_to_server():
    print("Connecting to server...")
    client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    client.connect(("00:e9:3a:68:c0:e8", 4))
    print("Connected to server!")
    return client

# socket
client = connect_to_server()

def send_message(message):
    client.send(message.encode('utf-8'))
    print("Message sent successfully!")


def register():
        mac_address = get_mac_address()
        print("MAC address:", mac_address)
        send_message(mac_address + "resgiter")


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
        send_message(id)
    except:
        print("Move Timeout")

    return redirect('/')


@app.route("/picture/")
def picture():
    try:
        send_message("QR code")
    except:
        print("Timeout")

    return redirect('/')


# run the app
if __name__ == "__main__":
    register()
    send()
    app.run(host='127.0.0.1', port=5000, debug=True)