#/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile

#SSL
__camera_port =     [8080, 8081, 8082, 8083]
__data_port =       [8090, 8091, 8092, 8093]
__cert_file =       'cert.pem'
__key_file =        'key.pem'

#Doesn't matter
echo = None

#################################################################

def rewrite():
    with tempfile.TemporaryFile(mode='r+') as tmp:
        with open('Pi/config.py') as configfile:
            for line in configfile:
                if '__' in line and not 'elif' in line:
                    tmp.write((line[0:21]))
                    print(tmp.read())
                    variable = line.split()[0]
                    tmp.write(str(eval(variable)))
                    tmp.write('\n')
                else:
                    tmp.write(line)
#        with open('Pi/config.py', 'wt+') as configfile:
#            for line in tmp:
#                print(line)
#                configfile.write(line)