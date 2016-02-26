#/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import tkinter
import queue
import collections
import os

def parse(raw):
    com_w_arg = raw.split(':')
    if len(com_w_arg) == 2:
        command, args = tuple(com_w_arg)
        command = command.strip()
        args = args.split(',')
        for i in range(0, len(args)):
            args[i] = args[i].strip()
            try:
                args[i] = int(args[i])
            except:
                pass
        return command, args
    elif len(com_w_arg) == 1:
        return raw, ['']
    else:
        return ' ', []

class Input(tkinter.Frame):

    def __init__(self, parent, read_queue, write_queue, stop):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.read_queue = read_queue
        self.write_queue = write_queue
        self.stop = stop
        self.command_list = collections.deque([])
        self.command_num = None
        self.current_command = ''
        self.deque = collections.deque([], 20)
        self.commands = {'help': self.help,
                         'quit': self.end,
                         'error': self.send_error,
                         'move': self.move,
                         'set safety': self.set_safety,
                         'fire': self.fire,
                         'move reticle': self.move_reticle,
                         'store location': self.store_location,
                         'get reticle': self.get_reticle,
                         'get altitude': self.get_altitude,
                         'get azimuth': self.get_azimuth,
                         'get safety': self.get_safety,
                         'get locations': self.get_locations,
                         '0x0': self.receive_error,
                         '0x10': self.receive_reticle,
                         '0x11': self.receive_altitude,
                         '0x12': self.receive_azimuth,
                         '0x13': self.receive_safety,
                         '0x14': self.receive_locations}
        self.ui_errors = {}
        self.pi_errors = {}
        self.parent.title('Command UI')
        self.input = tkinter.Entry(bg = 'black',
                                   foreground='white',
                                   font=('Courier', 12))
        self.logger = tkinter.Text(state=tkinter.DISABLED,
                                   bg = 'black',
                                   width = 100,
                                   height = 20,
                                   foreground='white',
                                   font=('Courier', 12))
        self.input.bind('<Return>', self.command)
        self.input.bind('<Up>', self.previous)
        self.input.bind('<Down>', self.next)
        self.input.pack(fill=tkinter.X)
        self.input.focus()
        self.logger.pack()
        self.parent.protocol('WM_DELETE_WINDOW', self.end)
        self.pack(fill = tkinter.BOTH, expand=True)
        self.poll()

    def end(self, *args):
        self.stop.set()
        self.parent.destroy()
        self.parent.quit()

    def command(self, *args):
        text = self.input.get()
        if len(self.command_list) == 0:
            self.command_list.append(text)
        elif text != self.command_list[len(self.command_list) - 1]:
            self.command_list.append(text)
        self.current_command = ''
        self.command_num = None
        self.input.delete(0, tkinter.END)
        command, arguments = parse(text)
        if command:
            try:
                self.commands[command](*arguments)
            except:
                self.log('ERR: Command "%s" not recognized. Enter ' %
                         command + '"help:" for a list of commands')
                raise

    def next(self, *args):
        if not (self.command_num == None or
                self.command_num == len(self.command_list) - 1):
            self.command_num += 1
            self.input.delete(0, tkinter.END)
            self.input.insert(tkinter.INSERT,
                              self.command_list[self.command_num])
        elif self.command_num == len(self.command_list) - 1:
            self.command_num = None
            self.input.delete(0, tkinter.END)
            self.input.insert(tkinter.INSERT, self.current_command)

    def previous(self, *args):
        if not (self.command_num == 0 or len(self.command_list) == 0):
            if self.command_num == None:
                text = self.input.get()
                self.current_command = text
                self.command_num = len(self.command_list) - 1
            else:
                self.command_num -= 1
            self.input.delete(0, tkinter.END)
            self.input.insert(tkinter.INSERT,
                              self.command_list[self.command_num])


    def log(self, message):
        self.deque.appendleft(message)
        self.logger.config(state=tkinter.NORMAL)
        text = ''
        for line in self.deque:
            text += line + '\n'
        self.logger.delete('1.0', tkinter.END)
        self.logger.insert(tkinter.INSERT, text)
        line_num = 1
        for line in self.deque:
            self.label(line_num, line[0:3])
            line_num += 1
        self.logger.update()
        self.logger.config(state=tkinter.DISABLED)

    def label(self, line, type):
        name = 'line' + str(line) + 'name'
        color = 'white'
        if type == 'RPi':
            color = 'turquoise'
        elif type == 'cmd':
            color = 'lime green'
        elif type == 'ERR':
            color = 'red'
        elif type == 'hel':
            color = 'medium orchid'
        self.logger.tag_add(name,
                            str(line)+'.0',
                            str(line)+'.5')
        self.logger.tag_config(name, foreground=color)

    def poll(self):
        if self.stop.is_set():
            self.end()
        if not self.read_queue.empty():
            q = self.read_queue.get()
            command = q.pop(0)
            args = q
            try:
                self.commands[command](args)
            except KeyError:
                self.log('ERR: Received unkown command code %s.' % command)
        self.after(250, self.poll)

    def help(self, *args):
        path = os.path.realpath(__file__)[:-6] + 'help/'
        if args[0] in ['help', '']:
            file = path +'help.txt'
        elif args[0] in self.commands:
            file = path + args[0].replace(' ', '_') + '.txt'
        else:
            self.log('ERR: "help" accepts only commands as parameters. ' +
                     'Enter "help:" for a list of commands')
            return
        with open(file) as help_text:
            for line in reversed(list(help_text)):
                self.log(line.rstrip())

    def send_error(self, *args):
        try:
            assert len(args) == 1
            code = args[0]
            try:
                self.log('ERR: ' + self.ui_errors[code])
                self.write_queue.put(['error', code])
            except:
                self.log('ERR: Tried to send unrecognized error code %s.' % code)
        except:
            self.log('ERR: Tried to send error with incorrect number of ' +
                     'arguments.')

    def move(self, *args):
        try:
            assert args[0] in ['pixel', 'location', 'altitude', 'azimuth']
            if args[0] == 'pixel':
                try:
                    assert len(args) == 2
                    assert isinstance(args[1], int)
                    self.write_queue.put(['move to pixel', args[1]])
                    self.log('cmd: Move to pixel #%s' % args[1])
                except:
                    self.log('ERR: "move" with the parameter "pixel" requires ' +
                             'a second integer parameter')
            elif args[0] in ['azimuth', 'altitude']:
                try:
                    assert len(args) == 3
                    assert args[1] in ['+', '=', '-']
                    assert isinstance(args[2], int)
                    assert args[2] >= 0
                    if args[1] == '=':
                        self.write_queue.put(['move to %s' % args[0], args[2]] )
                        self.log('cmd: Move to %s %s.' % (args[0], args[2]))
                    else:
                        change = args[2] if args[1] == '+' else args[2] * -1
                        cmd = ['change ' + args[0], change]
                        self.write_queue.put(item=cmd)
                        self.log('cmd: Change %s by %s.' % (args[0], change))
                except:
                    self.log('ERR: Command "move" with the parameter ' +
                             '%s requires a second operator ' % args[0] +
                             'parameter and a third integer positive parameter.')
            else:
                try:
                    assert len(args) == 2
                    assert isinstance(args[1], int)
                    assert args[1] >= 0
                    self.write_queue.put(['move to location', args[1]])
                    self.log('cmd: Move to location %s.' % args[1])
                except:
                    self.log('ERR: Command "move" with the parameter ' +
                             '"location" requires a second positive integer ' +
                             'parameter.')
        except:
            self.log('ERR: Command "move" requires a parameter specifying ' +
                     'type of movement. Enter "help:" for more information.')



    def set_safety(self, *args):
        try:
            assert len(args) == 1
            position = args[0]
            assert position in ['on', 'off']
            self.write_queue.put(['set safety', position])
            self.log('cmd: Set safety to %s.' % position)
        except:
            self.log('ERR: Command "set safety" requires a parameter of ' +
                     'either "on" or "off"')


    def fire(self, *args):
        self.write_queue.put('fire')
        self.log('cmd: Fire.')

    def move_reticle(self, *args):
        try:
            assert len(args) == 1
            assert isinstance(args[0], int)
            self.write_queue.put(['move reticle', args[0]])
            self.log('cmd: Move reticle to pixel %s.' % args[0])
        except:
            self.log('ERR: Command "move reticle" requires an integer ' +
                     'argument.')

    def store_location(self, *args):
        self.write_queue.put('store location')
        self.log('cmd: Store location.')

    def get_reticle(self, *args):
        self.write_queue.put('get reticle')
        self.log('cmd: Get reticle.')

    def get_altitude(self, *args):
        self.write_queue.put('get altitude')
        self.log('cmd: Get altitude.')

    def get_azimuth(self, *args):
        self.write_queue.put('get azimuth')
        self.log('cmd: Get azimuth.')

    def get_safety(self, *args):
        self.write_queue.put('get safety')
        self.log('cmd: Get safety position.')

    def get_locations(self, *args):
        self.write_queue.put('get locations')
        self.log('cmd: Get locations list.')

    def receive_error(self, arg):
        code = int.from_bytes(arg[0], 'big')
        try:
            self.log(self.pi_errors[code])
        except:
            self.log('ERR: Received unrecognized error code.')

    def receive_reticle(self, arg):
        pixel = int.from_bytes(arg[0], 'big')
        self.log('RPi: Reticle at pixel %s.' % pixel)

    def receive_altitude(self, arg):
        altitude = int.from_bytes(arg[0], 'big') / 100.0
        self.log('RPi: Altitude is %s°.' % altitude)

    def receive_azimuth(self, arg):
        azimuth = int.from_bytes(arg[0], 'big')/ 100.0
        self.log('RPi: Azimuth is %s°.' % azimuth)

    def receive_safety(self, arg):
        arg = int.from_bytes(arg[0], 'big')
        safety = 'on' if arg >= 15728640 else 'off'
        self.log('RPi: Safety is %s.' % safety)

    def receive_locations(self, arg):
        self.log('RPi: About to send locations.')