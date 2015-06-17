import Hardware.camera_controller as camera_controller
import socket
import time

host = ''
port = 4361
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host,port))
server_socket.listen(1)
with camera_controller.Camera_Constructor(server_socket) as controller:
    print('beginning transmission')
    controller.begin_transmission()
    time.sleep(10)
    print('done transmitting')