import tkinter as tk
import socket
import threading

from common import SERVER_BLE_ADDRESS

class RasptankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rasptank Control")
        self.geometry("400x300")

        self.client = None

        self.create_widgets()

        # Start a separate thread for receiving messages
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def create_widgets(self):
        # Create buttons for different movements
        directions = ["forward_left", "forward", "forward_right", "left", "right", "backward_left", "backward", "backward_right", "DS", "TS"]
        for direction in directions:
            btn = tk.Button(self, text=direction.replace("_", " ").title(), command=lambda dir=direction: self.send_message(dir))
            btn.pack(pady=5)

        # Button for scanning QR code
        qr_btn = tk.Button(self, text="Scan QR Code", command=self.scan_qr_code)
        qr_btn.pack(pady=10)

        # Text widget to display received messages
        self.text_box = tk.Text(self, height=5, width=40)
        self.text_box.pack(pady=10)

        # Connect to server
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.client.connect((SERVER_BLE_ADDRESS, 4))
            print("Connected to server!")
        except Exception as e:
            print(f"Failed to connect to server: {str(e)}")
            self.destroy()

    def send_message(self, message):
        try:
            if self.client:
                self.client.send(message.encode('utf-8'))
                print(f"Message '{message}' sent successfully!")
            else:
                print("Not connected to server!")
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

    def receive_messages(self):
        try:
            while True:
                if self.client:
                    message = self.client.recv(1024).decode('utf-8')
                    self.text_box.insert(tk.END, f"Received: {message}\n")
                    print(f"Received: {message}")
        except Exception as e:
            print(f"Error receiving message: {str(e)}")

    def scan_qr_code(self):
        try:
            self.send_message("qr-code")
        except Exception as e:
            print(f"Failed to scan QR code: {str(e)}")


if __name__ == "__main__":
    app = RasptankApp()
    app.mainloop()
