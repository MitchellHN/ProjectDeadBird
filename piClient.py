#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

host = '127.0.0.1'
port = 20533
size = 1024
msg = input('Hello Server!')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.send(msg)
data = s.recv(size)
s.close()
print ("Recieved: ")
print (data)

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
