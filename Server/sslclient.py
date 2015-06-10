#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl

host = '127.0.0.1'
port = 20533
size = 1024
msg = str.encode("Hello Server!")
ssl.PROTOCOL_TLSv1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wrap = ssl.wrap_socket(s, ca_certs="cert.pem", cert_reqs=ssl.CERT_REQUIRED)
wrap.connect((host, port))
wrap.send(msg)
data = bytes.decode(wrap.recv(size))
wrap.close()
print (data)
end = input('recieved')

"""
def main():
	
	return 0

if __name__ == '__main__':
	main()
"""
