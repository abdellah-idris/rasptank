import re
import socket
import threading

# Dictionnaire pour mapper les adresses MAC des clients aux sockets correspondantes
client_map = {}

# Dictionnaire pour mapper les contrôleurs aux robots
controller_robot_map = {}

def handle_client(client_socket, client_addr):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received from {client_addr}: {data.decode('utf-8')}")
            if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', data.decode('utf-8')):
                # Vérifier si le message est au format d'une adresse MAC Bluetooth
                handle_control_message(client_addr, data.decode('utf-8'))
            else:
                if client_addr in controller_robot_map:
                    send_to_specific_robot(controller_robot_map[client_addr], data)
    except OSError:
        pass
    print(f"Client {client_addr} disconnected")
    del client_map[client_addr]  # Supprimer l'entrée du client du dictionnaire
    client_socket.close()


def handle_control_message(controller_addr, message):
    # Si vous avez besoin de faire quelque chose spécifique avec les adresses MAC Bluetooth, ajoutez votre logique ici
    
    print(f"Received valid MAC address from controller {controller_addr}: {message}")
    controller_robot_map[controller_addr]=message
    if controller_addr in controller_robot_map:
        print(f"Controller {controller_addr} is linked to Robot {controller_robot_map[controller_addr]}")
    else:
        print(f"Controller {controller_addr} is not linked to any robot")

def send_to_specific_robot(controller_addr, message):
    print('mappage',controller_robot_map)
    if controller_addr in controller_robot_map:
        robot_addr = controller_robot_map[controller_addr]
        if robot_addr in client_map:
            robot_socket = client_map[robot_addr]
            try:
                robot_socket.send(message)
                print(f"Message sent to Robot {robot_addr}: {message}")
            except OSError:
                print(f"Failed to send message to Robot {robot_addr}")
    else:
        print(f"No robot linked to Controller {controller_addr}")


def client_handler(server_socket):
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            client_map[addr] = client_socket  # Ajouter l'adresse du client et le socket correspondant au dictionnaire
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down")

server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server.bind(("00:e9:3a:68:c0:e8", 4))  # Utilisation de l'interface par défaut sur le canal 4
server.listen(5)

print("Waiting for connections...")

try:
    client_handler(server)
except KeyboardInterrupt:
    print("Server is shutting down")
finally:
    server.close()