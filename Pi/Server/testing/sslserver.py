#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl

print ("Starting Pi Server")

host = ''
port = 20533
size = 1024
ssl.PROTOCOL_TLSv1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wrap = ssl.wrap_socket(s, server_side = True, certfile = 'cert.pem', keyfile = 'key.pem')
wrap.bind((host,port))
wrap.listen(1)
recvData = ''
while 1:
	client, address = wrap.accept()
	data = client.recv(size)
	if data:
		client.send(data)
		decoded = bytes.decode(data)
		print(decoded)
	client.close()

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
