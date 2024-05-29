from flask import Flask, render_template, redirect, url_for
import paho.mqtt.client as mqtt
from flask_mqtt import Mqtt
import uuid
import requests



tankID = None
team = ""
qrcode = ""
affichage = ""

app = Flask(__name__)


def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
    return mac

def register_with_dispatcher():
    print("connect ##############")
    mac_address = get_mac_address()
    print("mac adress : " + mac_address)

    response = requests.post("http://193.55.29.171:5500/connect", 
    json={"ip_adress": "1.0.0.10", "player_name" : "thiziri"})

    print("ddddd")
    response.raise_for_status()





@app.route("/")
def index():
    return render_template('client_ui.html', rasptank_ID=tankID, team=team, qrcode=qrcode, affichage=affichage)


@app.route("/move/<id>")
def move(id):
    try:
        print("TODO : send Move")
    except:
        print("Timeout")

    return redirect('/')


@app.route("/picture/")
def picture():
    try:
        mqtt.publish("picture" + tankID, "*")
    except:
        print("Timeout")

    return redirect('/')


# run the app
if __name__ == "__main__":
    register_with_dispatcher()
    app.run(host='127.0.0.1', port=5000, debug=True)