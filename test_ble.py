import socket
import threading
import subprocess
import re

def get_bluetooth_mac_address():
    try:
        # Utilise ipconfig pour obtenir des informations sur toutes les interfaces réseau
        output = subprocess.check_output("ipconfig /all", shell=True).decode('latin-1')

        # Recherche l'adresse MAC Bluetooth (généralement, elle contient 'Bluetooth' dans la description)
        mac_address = None
        for line in output.split('\n'):
            if 'Bluetooth' in line:
                match = re.search(r'(([A-Fa-f0-9]{2}[:-]){5}[A-Fa-f0-9]{2})', line)
                if match:
                    mac_address = match.group(0)
                    break

        return mac_address
    except subprocess.CalledProcessError as e:
        print("Failed to run ipconfig command:", e)
        return None

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
            message = input("Enter message: ")
            client_socket.send(message.encode('utf-8'))
    except OSError:
        pass
    print("Client disconnected")
    client_socket.close()

# mac_address = get_bluetooth_mac_address()
# if mac_address:
#     print(f"Server MAC Address: {mac_address}")
# else:
#     print("Unable to find Bluetooth MAC Address.")
#     exit(1)

server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server.bind(("00:e9:3a:68:c0:e8",4))  # Utilisation de l'interface par défaut sur le canal 4
server.listen(5)

print("Waiting for connections...")

try:
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
except KeyboardInterrupt:
    print("Server is shutting down")
finally:
    server.close()