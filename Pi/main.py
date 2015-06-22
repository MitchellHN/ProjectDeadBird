#/usr/bin/env python
# -*- coding: utf-8 -*-

#============================================================================
# Main
# ----
#   This is the main script for the Raspberry Pi Avicide system and initiates
#   all other necessary scripts and functions. It accepts some options.
#       -c, --no-camera         Removes camera function, replacing it with a
#                               dummy capability to provide necessary variables.
#       -e, --echo              Echo status updates and commands to the
#                               terminal.
#       -m, --no-motion         Removes motion function, replacing it with a
#                               dummy capability to provide necesaary variables.
#
#       -h, -?, --help          Displays help file.

import Server.piserver as piserver
import Hardware.camera_controller as camera_controller
import Hardware.motion_controller as motion_controller
import control
import socket
import ssl
import queue
import multiprocessing
import threading
import getopt
import getopt
import config
import sys


options, arguments = getopt.getopt(sys.argv[1:],
                                   'cmeh?', 
                                   ['no-camera', 
                                    'no-motion',
                                    'echo',
                                    'help'])

if '-h' in options or '--help' in options or '?' in options:
    helpfile = open('help.txt', 'w')
    print (helpfile.read)
    sys.exit()

motion = False if '-m' in options or '--no-motion' in options else True
camera = False if '-c' in options or '--no-camera' in options else True
echo = True if '-e' in options or '--echo' in options else False
config.echo = echo

camera_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                              socket.SOCK_STREAM), 
                                server_side = True, 
                                certfile = config.cert_file, 
                                keyfile = config.key_file)
data_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                            socket.SOCK_STREAM), 
                              server_side = True, 
                              certfile = config.cert_file, 
                              keyfile = config.key_file)
                              
camera_socket.bind('', config.camera_port)
data_socket.bind('', config.camera_port)
camera_socket.listen(1)
data_socket.listen(1)
with camera_controller.Camera_Constructor(camera_socket) as camera:
    motion = motion_controller.Motion_Controller(camera)
    camera_queue = queue.Queue()
    control_queue = queue.Queue()
    server_queue = queue.Queue()
    camera_thread = piserver.Camera_Process(camera, camera_queue, control_queue)
    server_thread = piserver.Server_Process(data_socket, 
                                            server_queue, 
                                            control_queue)
    control_thread = control.Control_Process(camera_queue, motion_controller, control_queue, server_queue)
    camera_thread.start()
    server_thread.start()
    control_thread.start()