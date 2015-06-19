#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing

class Control_Process (multiprocessing.Process):
	
	def __init__(self, camera_queue, motion_controller, read_queue, server_queue):
		self.camera_queue = camera_queue
		self.motion_controller = motion_controller
		self.read_queue = read_queue
		self.server_queue = server_queue
		
	def run(self):
		while True:
		    x = 1