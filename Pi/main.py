#/usr/bin/env python
# -*- coding: utf-8 -*-

import Server.piserver as piserver
import Hardware.camera_controller as camera_controller
import Hardware.motion_controller as motion_controller
import control
import socket
import ssl
import queue
import multiprocessing
import threading

CERTIFICATE = 'cert.pem'
KEY = 'key.pem'
CAMERA_PORT = 5392
DATA_PORT = 4532


camera_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                              socket.SOCK_STREAM), 
                                server_side = True, 
                                certfile = 'cert.pem', 
                                keyfile = 'key.pem')
data_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                            socket.SOCK_STREAM), 
                              server_side = True, 
                              certfile = 'cert.pem', 
                              keyfile = 'key.pem')
                              
camera_socket.bind('', CAMERA_PORT)
data_socket.bind('', DATA_PORT)
camera_socket.listen(1)
data_socket.listen(1)
with camera_controller.Camera_Constructor(camera_socket) as camera:
    motion = motion_controller.Motion_Controller(camera)
    camera_queue = queue.Queue()
    control_queue = queue.Queue()
    server_queue = queue.Queue()
    camera_thread = piserver.Camera_Process(camera, camera_queue, control_queue)
    server_thread = piserver.Server_Process(data_socket, 
                                            server_queue, 
                                            control_queue)
    control_thread = control.Control_Process(camera_queue, motion_controller, control_queue, server_queue)
    camera_thread.start()
    server_thread.start()
    control_thread.start()