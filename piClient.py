#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

host = '127.0.0.1'
port = 20533
size = 1024
msg = str.encode("Hello Server!")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.send(msg)
data = bytes.decode(s.recv(size))
s.close()
print (data)
end = input('recieved')

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
