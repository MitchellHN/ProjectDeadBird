#/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl
import multiprocessing

class Camera_Process (multiprocessing.process):
    
	def __init__(self, controller, port):
	    unwrapped_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    