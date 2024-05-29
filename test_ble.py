import bluetooth

# The address of the server (replace with your server's Bluetooth address)
server_address = "01:23:45:67:89:AB"

# Create a Bluetooth socket
client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Connect to the server
client_socket.connect((server_address, 1))

try:
    while True:
        # Send data to the server
        message = input("Enter message to send: ")
        if message.lower() == "quit":
            break
        client_socket.send(message)

        # Receive data from the server
        data = client_socket.recv(1024)
        print(f"Received: {data}")

except OSError:
    pass

print("Disconnected.")

# Close the socket
client_socket.close()
print("All done.")