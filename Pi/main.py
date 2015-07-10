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
#       -C, --static-config     The config file is not saved.
#       -p, --used-pins         Pins that are not to be used, separated by 
#                               semicolons.
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
import config
import sys

#Connects to a UI and executes commands received from it. 
#*Follows the protocol in Server/ssl_protocol.txt for connection.
#*Creates objects to control motion and camera.
#*Launches threads for camera, server, and control
#*Waits for a thread to terminate, then calls all threads to terminate.
#*Cleans up.
def connect_and_run():
    try:
        #Create data connection and wait for connection
        if config.echo:
            print('Connecting data')
        port_number = 0
        tried_ports = []
        #Create socket at open port, raise OSError if none are available
        while True:
            try:
                if config.echo:
                    print('Connecting on port %s' %
                          config.data_ports[port_number])
                data_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                                            socket.SOCK_STREAM), 
                                              server_side = True, 
                                              certfile = config._cert_file,
                                              keyfile = config._key_file)
                data_socket.bind(('', config.data_ports[port_number]))
                data_socket.listen(1)
                data_client, address = data_socket.accept()
                if config.echo:
                    print(address)
                    print('Connected to %r' % address[0])
            except OSError:
                if port_number < len(config.data_ports) - 1:
                    port_number += 1
                else:
                    print('ran out of ports')
                    raise
            else:
                break
        if config.echo:
            print('Waiting for camera port from UI.')
        #Wait for Port from UI
        while True:
            data = data_client.recv(3)
            if data:
                port = int.from_bytes(data, 'big')
                print(port)
                if port == 0:
                    config.camera_on = False
                    break
                if port not in tried_ports:
                    data_client.send(b'\xff')
                    break
                else:
                    data_client.send(b'\x00')
        #Connect to UI with camera connection
        if config.camera_on:
            if config.echo:
                print('Connecting camera')
            camera_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                                                          socket.SOCK_STREAM), 
                                            server_side = False, 
                                            certfile = config.cert_file, 
                                            keyfile = config.key_file)                              
            camera_socket.connect((address, port))
        else:
            camera_socket = None
            #Context manager for camera_controller
        with camera_controller.Camera_Constructor(camera_socket) as camera:
            #Create motion controller
            if config.motion_on:
                motion = motion_controller.Motion_Controller(camera)
            else:
                motion = motion_controller.Dummy_Motion_Controller(camera)
            #Add servos and actuators to motion controller
            motion.add_servo('altitude', 
                             config._altitude_pin,
                             config._altitude_range,
                             config._altitude_pulse,
                             config._altitude_reverse)
            motion.add_servo('azimuth', 
                             config._azimuth_pin,
                             config._azimuth_range,
                             config._azimuth_pulse,
                             config._azimuth_reverse)
            motion.add_actuator('trigger',
                                config._trigger_pin,
                                config._trigger_type)
            motion.add_actuator('safety',
                                config._safety_pin,
                                config._safety_type)
            #Create threads
            camera_queue = queue.Queue()
            control_queue = queue.Queue()
            server_queue = queue.Queue()
            stop_flag = threading.Event()
            threads = []
            camera_thread = piserver.Camera_Process(camera, 
                                                    camera_queue, 
                                                    control_queue,
                                                    stop_flag)
            server_thread = piserver.Server_Process(data_client,
                                                    server_queue, 
                                                    control_queue,
                                                    stop_flag)
            control_thread = control.Control_Process(camera_queue, 
                                                     motion, 
                                                     control_queue, 
                                                     server_queue,
                                                     stop_flag)
            #Start threads  
            if config.echo:
                print('Starting camera thread')
            camera_thread.start()
            threads.append(camera_thread)
            if config.echo:
                print('Starting server thread')
            server_thread.start()
            threads.append(server_thread)
            if config.echo:
                print('Starting control thread')
            control_thread.start()
            threads.append(control_thread)
            while True:
                alive = [i.is_alive() for i in threads]
                if not all(alive):
                    print('dying')
                    stop_flag.set()
                    break
            
    except:
        try:
            data_socket.close()
        except (UnboundLocalError, AttributeError):
            pass
        try:
            data_client.close()
        except (UnboundLocalError, AttributeError):
            pass
        try:
            camera_socket.close()
        except (UnboundLocalError, AttributeError):
            pass
        raise
        
#Handles options, including setting session variables in config
def handle_options():
    #Get and process options
    options, arguments = getopt.getopt(sys.argv[1:],
                                       'cCmeph?', 
                                       ['no-camera', 
                                        'no-motion',
                                        'echo',
                                        'help',
                                        'static-config',
                                        'used-pins'])
    #Set defaults
    config.camera_on = True
    config.motion_on = True
    config.echo = False
    if ('-e', '') in options or ('--echo', '') in options:
        config.echo = True
    else:
        config.echo = False
    for opt, arg in options:
        #Display help file
        if opt in ['-h', '--help', '-?']:
            with open('Pi/help.txt') as helpfile:
                print(helpfile.read())
            sys.exit()
        #Turn on or off echoing, motion control, and camera control according to
        #options given at command line.
        config.motion_on = False if opt in ['-m', '--no-motion'] else True
        config.camera_on = False if opt in ['-c', '--no-camera'] else True
        #Force disable camera if picamera isn't imported and motion if RPIO 
        #isn't imported.
        if not 'RPIO' in sys.modules:
            config.motion_on = False
        if not 'picamera' in sys.modules:
            config.camera_on = False
        if config.echo:
            print('Motion {0}'.format(('enabled' if config.motion_on 
                                       else 'disabled')))
        if config.echo:
            print('Camera {0}'.format(('enabled' if config.camera_on 
                                       else 'disabled')))
        #Disable rewriting the config file
        config.static = True if opt in ['-C', '--static-config'] else False
        #Reserve pins
        if opt in ['-p', '--used-pins']:
            config.used_pins = arg.replace(';' ' ').split()
        else:
            config.used_pins = []
            
def main():
    handle_options()
    #Connect to a UI and accept its commands
    connect_and_run()
    #Rewrite config
    if not config.static:
        config.rewrite()
    print('main thread over')
    
if __name__ == '__main__':    
    main()