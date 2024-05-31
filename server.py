import socket
import threading

from common import SERVER_BLE_ADDRESS
from mapping import CONTROLLER_ROBOT

# TODO :
#   -   Race Monitoring : QR Code
#   -   Stop : See teacher description : alternative, server stop a robot directly
#   -   Add a lock to nb_robot and nb_controller


NB_GROUP = 5
NB_LAPS = 2

is_start_race = False

nb_robot_lock = threading.Lock()
nb_controller_lock = threading.Lock()

nb_robot = 0
nb_controller = 0

# race tracker
race_tracker = {}

# Dictionnaire pour mapper les contrôleurs aux robots
controller_robot_map = CONTROLLER_ROBOT
robot_socket_map = {}
controller_socket_map = {}
robot_controller_map = {}


def send_to_specific_robot(address_controller, address_robot, message):
    global robot_socket_map
    if address_robot in robot_socket_map:
        sock = robot_socket_map[address_robot]
        try:
            sock.send(message.encode('utf-8'))
            print(f"Message sent to Robot {address_robot}: {message}")
        except OSError:
            print(f"Failed to send message to Robot {address_robot}")
    else:
        print(f"No robot linked to Controller {address_controller}")


def send_message(address, message):
    global robot_socket_map
    if address in robot_socket_map:
        sock = robot_socket_map[address]
        try:
            sock.send(message.encode('utf-8'))
            print(f"Message sent to Robot {address}: {message}")
        except OSError:
            print(f"Failed to send message to Robot {address}")
    elif address in controller_socket_map:
        sock = controller_socket_map[address]

        try:
            sock.send(message.encode('utf-8'))
            print(f"Message sent to Controller {address}: {message}")
        except OSError:
            print(f"Failed to send message to Robot {address}")
    else:
        print(f"Address {address} not identifiable")


def handle_client(client_socket, address):
    global controller_robot_map, robot_socket_map, is_start_race, nb_robot, nb_controller

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')

            print(f"Received from {address}: {message}")

            # message from controller
            if address in controller_robot_map:
                #  TODO : logic when we receive from controller
                # redirect to the robot
                address_robot = controller_robot_map[address]
                print(f"From controller {address} To robot {address_robot} Message :{message} ")

                if is_start_race:
                    send_to_specific_robot(address, address_robot, message) # send message to robot
                else:
                    send_message(address_robot, "no_start")  # sent to robot, no_start

            else:  # message received from robot
                # TODO : logic when we receive from robot
                print(f"Received from robot {address} Message : {message}")

                if "qr" in message.lower():
                    try:
                        qr_data = message.split(":")

                        race_tracker[address] = race_tracker[address]+1
                        nb_lap = race_tracker[address]
                        print(f"QR CODE Scanned : Robot {address} Completed {nb_lap}")

                    except Exception as e:
                        print(f"An error occurred: {e}")
    except OSError:
        print("OSError")

    finally:
        print(f"Client {address} disconnected")
        if address in controller_robot_map or address in controller_socket_map:
            nb_controller -= 1
            print(f"update controller count : nb_controller = {nb_controller}")
        else:
            nb_robot -= 1
            print(f"update robot count : nb_robot = {nb_robot}")

        client_socket.close()


def client_handler(server_socket):
    global nb_controller, nb_robot, is_start_race
    try:
        while True:
            client_socket, addr = server_socket.accept()
            
            address = addr[0]

            if address in controller_robot_map:
                print(f"Accepted connection from CONTROLLER  {address}")

                controller_socket_map[address] = client_socket

                with nb_controller_lock:
                    nb_controller += 1
                    print(f"nb_controller = {nb_controller}")
            else:
                print(f"Accepted connection from ROBOT {address}")

                robot_socket_map[address] = client_socket
                race_tracker[address] = 0  # init race tracker to 0 for robot

                with nb_robot_lock:
                    nb_robot += 1
                    print(f"nb_robot = {nb_robot}")

            # start the thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server is shutting down")


def race_handler():
    global is_start_race, nb_robot, nb_controller, NB_GROUP

    while not is_start_race:
        if nb_robot == nb_controller and nb_controller == NB_GROUP:           
            is_start_race = True
            for adress in robot_socket_map.keys():
                send_message(robot_socket_map, "start".encode('utf-8'))


if __name__ == "__main__":
    server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server.bind((SERVER_BLE_ADDRESS, 4))  # Utilisation de l'interface par défaut sur le canal 4
    server.listen(20)  # upgrade number of waiting connection

    print("Server Launched \n Waiting for connections...")

    race_thread = threading.Thread(target=race_handler, args=())
    race_thread.start()

    try:
        print("Start Server")
        client_handler(server)
    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        server.close()
