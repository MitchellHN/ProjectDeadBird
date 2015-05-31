#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
from random import randint
import time

print ("Starting threaded Pi Server")

#This thread listens for a client and stops when data is received from it.
class Send_Receive_Thread (threading.Thread):
	def __init__(self, threadID, name, server_socket, size, stop_event):
		threading.Thread.__init__(self)
		self.threadid = threadID
		self.name = name
		self.server_socket = server_socket
		self.stop_event = stop_event
		
	def run(self):
		recvData = ''
		print ('starting server')
		#Accept data from the client until some is actually received, then terminate the 
		while not self.stop_event.is_set():
			client, address = self.server_socket.accept()
			recvData = bytes.decode(client.recv(size))
			print (recvData)
			if recvData == 'Hello Server!':
				client.send(str.encode(recvData))
				self.stop_event.set()
				client.close()
		
		
#This class quotes Monty Python at you at a rate of 1 quote/second until stop_event is_set(). It will not stop on its own.
class Python_Thread (threading.Thread):
	def __init__(self, threadID, name, stop_event):
		threading.Thread.__init__(self)
		self.threadid = threadID
		self.name = name
		self.stop_event = stop_event
		
	def run(self):
		count = 0
		pyquotes = ["Hello", "my", "name", "is", "bob", "and", "I", "am", "a", "happy", "person"]
				
		while not self.stop_event.is_set():
			print (pyquotes[randint(0, len(pyquotes) - 1)])
			print ("\n")
			print (self.stop_event.is_set())
			time.sleep(1)

    	

def set_up_socket():
	host = ''
	port = 20533
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((host,port))
	server_socket.listen(1)
	return server_socket


server_socket = set_up_socket()
stop_event = threading.Event()
py_thread = Python_Thread(1, 'thread 1', stop_event)
size = 1024
server_thread = Send_Receive_Thread(2, 'thread 2', server_socket, size, stop_event)

server_thread.start()
py_thread.start()


"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
