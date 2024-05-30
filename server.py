import socket
import threading


# TODO :
#   -   QR Code
#   -   Race Monitoring


# Dictionnaire pour mapper les contrôleurs aux robots
controller_robot_map = {}
robot_socket_map = {}
controller_socket_map = {}
robot_controller_map = {}


def handle_client(client_socket, address):
    global controller_robot_map, robot_socket_map

    while True:
        data = client_socket.recv(1024)
        if not data:
            client_socket.send("Authentication failed...Please reconnect")
            break

        message = data.decode('utf8')

        if message == "robot":
            # add address to
            print(f"From robot {address}")
            robot_socket_map[address] = client_socket

        else:
            address_robot = message
            print(f"from controller {address} associated to robot {address_robot}")

            controller_socket_map[address] = client_socket
            controller_robot_map[address] = address_robot  # message here is the robot address
            robot_controller_map[address_robot] = address  # message here is the robot address

        break  # break fisrt while loop when f

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
                send_to_specific_robot(address, address_robot, message)

            elif address in robot_controller_map:
                # TODO : logic when we receive from robot
                address_controller = robot_controller_map[address]
                print(f"Received from robot {address} To controller {address_controller} Message : {message}")

    except OSError:
        print("OSError")

    finally:
        print(f"Client {address} disconnected")
        # TODO : Supprimer l'entrée du client du dictionnaire associé
        client_socket.close()


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


def client_handler(server_socket):
    try:
        while True:
            client_socket, addr = server_socket.accept()
            address = addr[0]

            print(f"Accepted connection from {address}")

            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Server is shutting down")


if __name__ == "__main__":
    server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server.bind(("00:e9:3a:68:c1:04", 4))  # Utilisation de l'interface par défaut sur le canal 4
    server.listen(20)  # upgrade number of waiting connection

    print("Server Launched \n Waiting for connections...")

    try:
        client_handler(server)
    except KeyboardInterrupt:
        print("Server is shutting down")
    finally:
        server.close()
