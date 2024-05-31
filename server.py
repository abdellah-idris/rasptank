import socket
import threading
import random
import time

from common import SERVER_BLE_ADDRESS
from mapping import CONTROLLER_ROBOT, ROBOT_CONTROLLER

# TODO :
#   -   Race Monitoring : QR Code
#   -   Stop : See teacher description : alternative, server stop a robot directly
#   -   Add a lock to nb_robot and nb_controller


NB_GROUP = 1
NB_LAPS = 2

# Global variables
is_start_race = False

nb_robot_lock = threading.Lock()
nb_controller_lock = threading.Lock()

nb_robot = 0
nb_controller = 0

# Trackers and maps
race_tracker = {}

# Dictionnaire pour mapper les contrôleurs aux robots
controller_robot_map = CONTROLLER_ROBOT
robot_controller_map = ROBOT_CONTROLLER

robot_socket_map = {}
controller_socket_map = {}
blocked_robots = {}  # To track blocked robots and unblock time


time_block = 2
time_choice = time_block+20

winners = []

# Send message to a specific robot
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


# Send message to a robot or controller
def send_message(address, message):
    global robot_socket_map, controller_socket_map
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
            print(f"Failed to send message to Controller {address}")
    else:
        print(f"Address {address} not identifiable")


# Handle client connection
def handle_client(client_socket, address):
    global controller_robot_map, robot_socket_map, is_start_race, nb_robot, nb_controller, robot_controller_map

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')
            print(f"Received from {address}: {message}")

            if address in controller_robot_map:
                address_robot = controller_robot_map[address]
                print(f"From controller {address} To robot {address_robot} Message :{message}")

                if is_start_race:
                    send_to_specific_robot(address, address_robot, message)
                else:
                    send_message(address, "Race did not started yet")

            else:  # message from robot
                try:
                    address_controller = robot_controller_map[address]
                    race_tracker[address_robot] = race_tracker[address_robot]+1
                    print(f"Received from robot {address} To controller {address_controller} Message : {message}")

                    send_message(address_controller, message.split(":")[1])

                    if (race_tracker[address_robot]==2):
                        winners.append(address_robot)

                except Exception as e:
                    print(f"Error when Send QR to controller. Error {e} ")

            if(len(winners)==NB_GROUP):
                print("The END")
                for i in range(0,len(winners)):
                    if (i==0):
                        send_message(winners[0], "You are the Winner")
                    else:
                        send_message(winners[i], "classified: ", i)

    except OSError:
        print("OSError")

    finally:
        print(f"Client {address} disconnected")
        if address in controller_robot_map or address in controller_socket_map:
            nb_controller -= 1
            print(f"update controller count = nb_controller = {nb_controller}")
        else:
            nb_robot -= 1
            print(f"update robot count = nb_robot = {nb_robot}")

        client_socket.close()


# Client handler function
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


# Race handler function
def race_handler():
    global is_start_race, nb_robot, nb_controller, NB_GROUP

    while not is_start_race:
        if nb_robot == nb_controller and nb_controller == NB_GROUP:
            is_start_race = True
            for address in robot_socket_map.keys():
                send_message(address, "start")


# Select and block a random robot
def block_random_robot():
    global blocked_robots, robot_socket_map, is_start_race

    if is_start_race:
        robots = list(robot_socket_map.keys())
        if not robots:
            print("BLock method: No robots connected.")
            return

        # available_robots = [robot for robot in robots if robot not in blocked_robots]
        # if not available_robots:
        #     print("All robots are currently blocked.")
        #     return

        chosen_robot = random.choice(robots)
        blocked_robots[chosen_robot] = time.time() + time_block
        send_message(chosen_robot, "BLOCK")
        print(f"Robot {chosen_robot} is blocked for ",time_block," seconds.")


# Block handler function
def block_handler():
    while True:
        block_random_robot()
        time.sleep(time_choice)  # Wait 5 seconds of blocking time + 3 seconds


if __name__ == "__main__":
    server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server.bind((SERVER_BLE_ADDRESS, 4))
    server.listen(20)

    print("Server Launched \n Waiting for connections...")

    race_thread = threading.Thread(target=race_handler, args=())
    race_thread.start()

    block_thread = threading.Thread(target=block_handler, args=())
    block_thread.start()

    try:
        print("Start Server")
        client_handler(server)
    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        server.close()
