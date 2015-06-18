#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl
import multiprocessing
import threading
import queue

class Camera_Process (multiprocessing.Process):
    
	def __init__(self, camera_controller, queue):
	    self.camera_controller = camera_controller
	    self.queue = queue
	
	def run(self):
		while True:
			if not self.queue.empty():
				q = self.queue.get()

class Control_Process (multiprocessing.Process):
	
	def __init__(self, camera_controller, motion_controller, socket, port, 
				 camera_queue):
		self.camera_controller = camera_controller
		unwrapped_socket = socket
		self.socket = ssl.wrap_socket(unwrapped_socket,
										 server_side = True,
										 certfile = 'cert.pem',
										 keyfile = 'key.pem')
		self.socket.bind('', port)
		self.camera_queue = camera_queue
		self.server_thread = Server_Thread(socket)
		
	def run(self):
		queue = queue.Queue()
		server_thread = Server_Thread(self.socket, queue)
		
		
		
class Server_Thread (threading.Thread):
	
	def __init__(self, socket, queue):
		self.socket = socket
		self.queue = queue
		
	def run(self):
		while True:
			