import socket
#import move

# Bluetooth client setup
server_mac_address = "00:e9:3a:68:c0:e8"
port = 4
client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

print(f"Connecting to {server_mac_address} on port {port}...")

try:
    client.connect((server_mac_address, port))
    print("Connected successfully!")
    # Send initial message "ROBOT"
    client.send("ROBOT".encode('utf-8'))
    print("Initial message sent: ROBOT")
except OSError as e:
    print(f"Connection error: {e}")
    client.close()
    exit(1)

#move.setup()
direction_command = 'no'
turn_command = 'no'

functionMode = 0
speed_set = 100
rad = 0.5
turnWiggle = 60

def robotCtrl(command_input):
    global direction_command, turn_command
    if 'forward' == command_input:
        direction_command = 'forward'
        turn_command='no'
        print("forward")
        #move.move(speed_set, direction_command, turn_command, rad)

    elif 'forward_left' == command_input:
        direction_command = 'forward'
        turn_command='left'
        print("forward_left")
        #move.move(speed_set, direction_command, turn_command, rad)
    elif 'forward_right' == command_input:
        direction_command = 'forward'
        turn_command='rigth'
        print("forward_right")
        #move.move(speed_set, direction_command, turn_command, rad)
    
    elif 'backward' == command_input:
        direction_command = 'backward'
        turn_command = 'no'
        #move.move(speed_set, direction_command, turn_command, rad)
        print("backward")
    elif 'backward_left' == command_input:
        direction_command = 'backward'
        turn_command='left'
        print("backward_left")
        #move.move(speed_set, direction_command, turn_command, rad)
    elif 'backward_right' == command_input:
        direction_command = 'backward'
        turn_command='right'
        print("backward_right")
        #move.move(speed_set, direction_command, turn_command, rad)

    elif 'DS' in command_input:
        direction_command = 'no'
        #move.move(speed_set, direction_command, turn_command, rad)
        print("DS")

    elif 'left' == command_input:
        direction_command = 'no'
        turn_command = 'left'
        #move.move(speed_set, direction_command, turn_command, rad)
        print("left")

    elif 'right' == command_input:
        direction_command = 'no'
        turn_command = 'right'
        #move.move(speed_set, direction_command, turn_command, rad)
        print("right")

    elif 'TS' in command_input:
        turn_command = 'no'
        #move.move(speed_set, direction_command, turn_command, rad)
        print("TS")

    elif 'qr-code' == command_input:
        print("qr-code")
    


def recv_msg():
    global speed_set, direction_command,turn_command
    #move.setup()
    direction_command = 'no'
    turn_command = 'no'

    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
            command_input = data.decode('utf-8')
            print(f"Received command: {command_input}")
            if isinstance(command_input, str):
                robotCtrl(command_input)
    except OSError as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    recv_msg()
