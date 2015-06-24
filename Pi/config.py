#/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os

#SSL
__data_ports =          [8090, 8091, 8092, 8093]
__cert_file =           'cert.pem'
__key_file =            'key.pem'

#IO
__altitude_pin =        1
__altitude_rangev =     90
__altitude_pulse =      [1.0, 2.0]
__altitude_reverse =    False
__azimuth_pin =         2
__azimuth_rangev =      90
__azimuth_pulse =       [1.0, 2.0]
__azimuth_reverse =     False
__trigger_pin =         3
__trigger_type =        'pull'
__safety_pin =          4
__safety_type =         'pull'
__safety_on_position =  'out'

#Formulas -- do not change
self_path = os.path.realpath(__file__)
path = self_path[:(-1*len(__file__))]

#Sesion Variables -- initialized in script
echo = None
used_pins = None
static = None
motion_on = None
camera_on = None

def rewrite():
    #Open config script, closing even with an exception.
    with open(self_path) as configfile:
        #Create empty file string
        tmp = ''
        for line in configfile:
            #Variable lines
            if line[0:2] == '__':
                #Add everything but the value
                tmp += (line[0:24])
                variable = line.split()[0]
                #Add the variable
                if isinstance(eval(variable), str):
                    variable = "'" + str(eval(variable)) + "'"
                else:
                    variable = str(eval(variable))
                tmp += variable
                tmp += '\n'
            #Non-variable lines
            else:
                #Add line as-is
                tmp += line
    #Open config script, write over it, closing even with an exception.
    with open(self_path, 'w+') as configfile:
        configfile.write(tmp)