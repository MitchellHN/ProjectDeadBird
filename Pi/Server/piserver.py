#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl
import multiprocessing
import threading
import queue

class Camera_Process (threading.Thread):
    			
	def __init__(self, camera_controller, read_queue, control_queue):
	    self.camera_controller = camera_controller
	    self.read_queue = read_queue
	    self.control_queue = control_queue
	    self.commands = {'start': self.start_camera,
	    				 'stop': self.stop_camera,
	    				 'get callibration': self.get_calibration,
	    				 'calibrate': self.calibrate}
	
	def run(self):
		while True:
			if not self.read_queue.empty():
				#Get command from queue
				q = self.read_queue.get()
				#Extract command and arguments (if any)
				if isinstance(q, list):
					command = q.pop(0)
					arguments = q
				elif isinstance(q, str):
					command = q
					arguments = []
				else:
					raise TypeError('Something other than list or str was ' + 
									 'added to the camera queue.')
				#Try to execute command, raise errors if necessary
				try:
					self.commands[command](*arguments)
				except KeyError:
					print("%r is not an acceptable camera command" % command)
				except TypeError:
					message = "The %r command was given the arguments %r" % (command, arguments)
					print(message)
					raise
					
					
	def start_camera(self):
		self.camera_controller.begin_transmission()
		
	def stop_camera(self):
		self.camera_controller.end_transmission()
	
	def get_calibration(self):
		command = ['calibration ==', self.camera_controller.crosshair_calibration]
		self.control_queue.put(command)
		
	def calibrate(self, x, y):
		self.camera_controller.crosshair_calibration = [x, y]
		
					
				

class Server_Process (threading.Thread):
	
	def __init__(self, socket, read_queue, control_queue):
		self.socket = socket
		self.read_queue = read_queue
		self.control_queue = control_queue
		self.send_queue = queue.Queue()
		self.receive_queue = queue.Queue()
		self.send_thread = Send_Thread(socket, self.send_queue)
		self.receive_thread = Receive_Thread(socket, self.receive_queue)
		self.commands = {''''0x00': self.receive_error,
						 '0x10': self.move_to_pixel,
						 '0x11': self.move_to_altitude,
						 '0x12': self.change_altitude,
						 '0x13': self.move_to_azimuth,
						 '0x14': self.change_azimuth,
						 '0x15': self.move_to_location,
						 '0x16': self.set_safety,
						 '0x17': self.fire,
						 '0x30': self.move_reticle,
						 '0x31': self.store_location,
						 '0x50': self.get_reticle,
						 '0x51': self.get_altitude,
						 '0x52': self.get_azimuth,
						 '0x53': self.get_safety,
						 '0x54': self.get_locations'''}
		
	def run(self):
		self.send_thread.start()
		self.receive_thread.start()
		while True:
			if not self.read_queue.empty():
				self.interpret_read()
			if not self.receive_queue.empty():
				self.interpret_receive()
				
	def interpret_read(self):
		#Get command from queue
		q = self.read_queue.get()
		#Extract command and arguments (if any)
		if isinstance(q, list):
			command = q.pop(0)
			arguments = q
		elif isinstance(q, str):
			command = q
			arguments = []
		else:
			raise TypeError('Something other than list or str was ' + 
							 'added to the camera queue.')
		#Try to execute command, raise errors if necessary
		try:
			self.commands[command](*arguments)
		except KeyError:
			print("%r is not an acceptable camera command" % command)
		except TypeError:
			message = "The %r command was given the arguments %r" % (command, arguments)
			print(message)
			raise
		
	def interpret_receive(self):
		#Get command from queue
		q = self.receive_queue.get()
		#Extract command and arguments (if any)
		if isinstance(q, list):
			command = q.pop(0)
			arguments = q
		elif isinstance(q, str):
			command = q
			arguments = []
		else:
			raise TypeError('Something other than list or str was ' + 
							 'added to the camera queue.')
		#Try to execute command, raise errors if necessary
		try:
			self.commands[command](*arguments)
		except KeyError:
			print("%r is not an acceptable camera command" % command)
		except TypeError:
			message = "The %r command was given the arguments %r" % (command, arguments)
			print(message)
			raise
				
class Send_Thread (threading.Thread):
	
	def __init__(self, socket, read_queue):
		self.socket = socket
		self.read_queue = read_queue
		self.commands = {}
		
	def run(self):
		while True:
			if not self.read_queue.empty():
				#Get command from queue
				q = self.read_queue.get()
				#Extract command and arguments (if any)
				if isinstance(q, list):
					command = q.pop(0)
					arguments = q
				elif isinstance(q, str):
					command = q
					arguments = []
				else:
					raise TypeError('Something other than list or str was ' + 
									 'added to the camera queue.')
				#Try to execute command, raise errors if necessary
				try:
					self.commands[command](*arguments)
				except KeyError:
					print("%r is not an acceptable camera command" % command)
				except TypeError:
					message = "The %r command was given the arguments %r" % (command, arguments)
					print(message)
					raise
		
class Receive_Thread (threading.Thread):
	
	def __init__(self, socket, master_queue):
		self.socket = socket
		self.master_queue = master_queue
		
	def run(self):
		while True:
			data = self.socket.recv(4)
			if data:
				command = hex(data[0])
				argument = bytes([data[1], data[2], data[3]])
				self.master_queue.put([command, argument])
				