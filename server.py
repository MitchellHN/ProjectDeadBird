#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

print ("Starting Pi Server")

host = ''
port = 20533
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(1)
recvData = ''
while 1:
	client, address = s.accept()
	data = client.recv(size)
	if data:
		client.send(data)
	client.close()

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
