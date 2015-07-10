# /usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================================================
# Pi Server
# ----
#   This script contains the classes necessary to deliver video and commands
#	to the UI and receive commands back.

import socket
import ssl
import multiprocessing
import threading
import queue
import config

# Used to pipe the video feed to the UI
class Camera_Process(threading.Thread):
    # Creation method
    #   camera_controller:
    #       The camera controller object. Camera_Controller.
    #	read_queue:
    #		The queue from which the thread pulls instructions. queue.Queue.
    #	control_queue:
    #		The queue to which the thread pushes instructions. queue.Queue.
    #	stop_flag:
    #		When set, the thread terminates. threading.Event
    def __init__(self, camera_controller, read_queue, control_queue, stop_flag):
        threading.Thread.__init__(self, name = 'camera')
        self.camera_controller = camera_controller
        self.read_queue = read_queue
        self.stop_flag = stop_flag
        self.control_queue = control_queue
        self.commands = {'start': self.start_camera,
                         'stop': self.stop_camera,
                         'get reticle': self.get_calibration,
                         'move reticle': self.calibrate}

    # Main process. Do not call; use start() instead.
    def run(self):
        while True:
            if self.stop_flag.is_set():
                break
            if not self.read_queue.empty():
                # Get command from queue
                q = self.read_queue.get()
                # Extract command and arguments (if any)
                if isinstance(q, list):
                    command = q.pop(0)
                    arguments = q
                elif isinstance(q, str):
                    command = q
                    arguments = []
                else:
                    raise TypeError('Something other than list or str was ' +
                                    'added to the camera queue.')
                # Try to execute command, raise errors if necessary
                try:
                    self.commands[command](*arguments)
                except KeyError:
                    print("%r is not an acceptable camera command" % command)
                except TypeError:
                    message = "The %r command was given the arguments %r" % (command, arguments)
                    print(message)
                    raise

    # Starts the camera_controller
    def start_camera(self):
        self.camera_controller.begin_transmission()

    # Stops the camera_controller
    def stop_camera(self):
        self.camera_controller.end_transmission()

    # Get and return calibration
    def get_calibration(self):
        command = ['reticle ==']
        command += self.camera_controller.crosshair_calibration
        self.control_queue.put(command)

    # Change calibration
    def calibrate(self, x, y):
        self.camera_controller.crosshair_calibration = [x, y]


# Used to send commands to and receive commands from the UI.Creates child threads
# Send_Thread and Receive_Thread, and terminates them as necessary.
class Server_Process(threading.Thread):
    # Creation method
    #   socket:
    #       The bound data socket. Socket.
    #	read_queue:
    #		The queue from which the thread pulls instructions. queue.Queue.
    #	control_queue:
    #		The queue to which the thread pushes instructions. queue.Queue.
    #	stop_flag:
    #		When set, the thread terminates. threading.Event
    def __init__(self, socket, read_queue, control_queue, stop_flag):
        threading.Thread.__init__(self, name = 'server')
        self.socket = socket
        self.stop_flag = stop_flag
        self.child_stop_flag = threading.Event()
        self.send_thread = Send_Thread(socket,
                                       read_queue,
                                       self.child_stop_flag)
        self.receive_thread = Receive_Thread(socket,
                                             control_queue,
                                             self.child_stop_flag)

    # Main process. Do not call; use start() instead.
    def run(self):
        threads = []
        self.send_thread.start()
        self.receive_thread.start()
        while True:
            if self.stop_flag.is_set():
                self.child_stop_flag.set()
                break
            alive = [i.is_alive() for i in threads]
            if self.child_stop_flag.is_set() or not all(alive):
                self.child_stop_flag.set()
                self.stop_flag.set()


# Used to send commands to the UI. Converts from [command, argument] pair to
# bytes and sends to the UI.
class Send_Thread(threading.Thread):
    # Creation method
    #   client:
    #       The bound data socket. Socket.
    #	read_queue:
    #		The queue from which the thread pulls instructions. queue.Queue.
    #	stop_flag:
    #		When set, the thread terminates. threading.Event
    def __init__(self, client, read_queue, stop_flag):
        threading.Thread.__init__(self, name = 'send')
        self.client = client
        self.read_queue = read_queue
        self.stop_flag = stop_flag
        self.commands = {'send_error': self.send_error,
                         'send reticle': self.send_reticle,
                         'send altitude': self.send_altitude,
                         'send azimuth': self.send_azimuth,
                         'send safety': self.send_safety,
                         'send locations': self.send_locations}

    # Main process. Do not call; use start() instead.
    def run(self):
        while True:
            if self.stop_flag.is_set():
                break
            if not self.read_queue.empty():
                # Get command from queue
                q = self.read_queue.get()
                # Extract command and arguments (if any)
                if isinstance(q, list):
                    command = q.pop(0)
                    arguments = q
                elif isinstance(q, str):
                    command = q
                    arguments = []
                else:
                    raise TypeError('Something other than list or str was ' +
                                    'added to the camera queue.')
                # Try to execute command, raise errors if necessary
                try:
                    self.commands[command](*arguments)
                except KeyError:
                    print("%r is not an acceptable send command" % command)
                except TypeError:
                    message = ("The %r command was given the arguments %r" %
                               (command, arguments))
                    print(message)
                    raise

    def send_error(self, error_ID):
        if config.echo:
            print ('Sending error code %s.' % error_ID)
        self.send(0, error_ID)

    def send_reticle(self, pixel_number):
        if config.echo:
            print ('Sending reticle == %s.' % pixel_number)
        self.send(16, pixel_number)

    def send_altitude(self, altitude):
        self.send(17, int(altitude * 100))

    def send_azimuth(self, azimuth):
        self.send(18, int(azimuth * 100))

    def send_safety(self, safety):
        argument = bytes.fromhex('ffffff') if safety == 'on' else bytes(3)
        self.send(19, argument)

    def send_locations(self, locations):
        pass

    def send(self, command, argument, is_signed=False):
        assert type(argument) in [int, bytes]
        if isinstance(argument, int):
            argument = argument.to_bytes(3, 'big', signed=is_signed)
        message = command.to_bytes(1, 'big') + argument
        if config.echo:
            print('Sending byte code %s.' % message)
        self.client.send(message)


class Receive_Thread(threading.Thread):
    def __init__(self, socket, control_queue, stop_flag):
        threading.Thread.__init__(self, name = 'receive')
        self.socket = socket
        self.control_queue = control_queue
        self.stop_flag = stop_flag
        self.commands = {'0x0': self.receive_error,
                         '0x10': self.move_to_pixel,
                         '0x11': self.move_to_altitude,
                         '0x12': self.change_altitude,
                         '0x13': self.move_to_azimuth,
                         '0x14': self.change_azimuth,
                         '0x15': self.move_to_location,
                         '0x16': self.set_safety,
                         '0x17': self.fire,
                         '0x30': self.move_reticle,
                         '0x31': self.store_location,
                         '0x50': self.get_reticle,
                         '0x51': self.get_altitude,
                         '0x52': self.get_azimuth,
                         '0x53': self.get_safety,
                         '0x54': self.get_locations}
        self.errors = {
        }

    # Main process. Do not call; use start() instead.
    def run(self):
        while True:
            if self.stop_flag.is_set():
                break
            data = self.socket.recv(4)
            if data:
                print(data)
                command = hex(data[0])
                argument = bytes([data[1], data[2], data[3]])
                if config.echo:
                    print('Received command %s with argument %s' % (command,
                                                                    argument))
        # Try to execute command, raise errors if necessary
                    try:
                        self.commands[command](argument)
                    except KeyError:
                        print("%r is not an acceptable byte command." % command)
                    except TypeError:
                        message = "The %r command was given the argument %r." % (command,
                                                                                 argument)
                        print(message)
                    except:
                        raise

    def receive_error(self, error):
        # get hex string
        error = hex(int.from_bytes(error, 'big'))
        self.control_queue.put(['error', self.errors[error]])

    def move_to_pixel(self, pixel):
        pixel_number = int.from_bytes(pixel, byteorder='big')
        if config.echo:
            print('Received command to move to pixel %s.' % pixel_number)
        self.control_queue.put(['move to pixel', pixel_number])

    def move_to_altitude(self, altitude):
        altitude = int.from_bytes(altitude, byteorder='big')
        altitude /= 100.0
        if config.echo:
            print('Received command to move to altitude %s.' % altitude)
        self.control_queue.put(['move to altitude', altitude])

    def change_altitude(self, change):
        change = int.from_bytes(change, byteorder='big', signed=True)
        change /= 100.0
        if config.echo:
            print('Received command to change altitude by %s.' % change)
        self.control_queue.put(['change altitude', change])

    def move_to_azimuth(self, azimuth):
        azimuth = int.from_bytes(azimuth, byteorder='big')
        azimuth /= 100.0
        if config.echo:
            print('Received command to move to azimuth %s.' % azimuth)
        self.control_queue.put(['move to azimuth', azimuth])

    def change_azimuth(self, change):
        change = int.from_bytes(change, byteorder='big', signed=True)
        change /= 100.0
        if config.echo:
            print('Received command to change azimuth by %s.' % change)
        self.control_queue.put(['change azimuth', change])

    def move_to_location(self, location):
        if config.echo:
            print('Received command to move to location %s.' %
                  int.from_bytes(location, 'big'))
        self.control_queue.put(['move to location',
                                 int.from_bytes(location, 'big')])

    def set_safety(self, on_off):
        # If the first bit is 1, i.e. >= i.e. 1000 0000 0000 0000 0000 0000 in
        # binary, turn the safety on
        if int.from_bytes(on_off, 'big') >= 8388608:
            position = 'on'
        else:
            position = 'off'
        if config.echo:
            print('Received command to set safety %s.' % position)
        self.control_queue.put(['set safety', position])

    def fire(self, irrelevant):
        if config.echo:
            print('Received command to fire.')
        self.control_queue.put('fire')

    def move_reticle(self, pixel):
        pixel_number = int.from_bytes(pixel, byteorder='big')
        if config.echo:
            print('Received command to set reticle to pixel %s.' % pixel_number)
        self.control_queue.put(['move reticle', pixel_number])

    def store_location(self, irrelevant):
        if config.echo:
            print('Received command to set reticle to store location.')
        self.control_queue.put('store location')

    def get_reticle(self, irrelevant):
        if config.echo:
            print('Received command to get reticle position.')
        self.control_queue.put('send reticle')

    def get_altitude(self, irrelevant):
        if config.echo:
            print('Received command to get altitud.')
        self.control_queue.put('send altitude')

    def get_azimuth(self, irrelevant):
        if config.echo:
            print('Received command to get azimuth.')
        self.control_queue.put('send azimuth')

    def get_safety(self, irrelevant):
        if config.echo:
            print('Received command to get safety position.')
        self.control_queue.put('send safety')

    def get_locations(self, irrelevant):
        if config.echo:
            print('Received command to get list of saved locations.')
        self.control_queue.put('send locations')
