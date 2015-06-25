#/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os

#============================================================================
# Config
# ----
#   This file stores variables from session to session, is used to store
#   session variables, and rewrites itself if its values change. There are
#   a few rules that must be followed to ensure that the file is correctly
#   updated:
#       *All variables that are stored from session to session must have names
#        beginnging with "__".
#       *The variable names and the equals sign must finish before column 25.
#       *Variable values must begin on or after column 25.
#       *Lists and dictionaries may be split across multiple lines, as normal.
#       *In-line comments are okay, but should be confined to a single line.
#       *Lists and dictionaries may have a comment on only one line, even if
#        their values are split across multiple lines.
#       *Because comments will begin no later than column 53, they should be
#        no longer than 28 characters long, including the '#'. Longer comments
#        will not result in errors or strange behavior, but will result in a
#        line that is longer than the preferred 80 characters max.
#       *The rewrite() function absolutely MUST be preceded by a line that
#        contains '###.
#   
#   When this file is updated, if a variable has been changed to a value that 
#   cannot be written as a literal it and any comments are written as found in
#   the last successfully updated version of the file.
#
#   Note that after updating, lists and dictionaries will be split across
#   multiple lines and comments may be moved, either to column 53, to the 
#   first line of a dictionary or list, or both.

#SSL
__data_ports =          [8090,                      #list of possible ports
                         8091,
                         8092,
                         8093]
__cert_file =           'cert.pem'
__key_file =            'key.pem'

#IO
__altitude_pin =        1
__altitude_rangev =     90
__altitude_pulse =      [1.0,
                         2.0]
__altitude_reverse =    False
__azimuth_pin =         2
__azimuth_rangev =      90
__azimuth_pulse =       [1.0,
                         2.0]
__azimuth_reverse =     False
__trigger_pin =         3
__trigger_type =        'pull'
__safety_pin =          4
__safety_type =         'pull'
__safety_on_position =  'out'

##################Do Not Edit Past This Line##################

self_path = os.path.realpath(__file__)
path = self_path[:-9]

#Rewrite this config file. 
def rewrite():
    unwriteable = []
    #Open config script, closing even with an exception.
    with open(self_path) as configfile:
        #Get comments
        comments = {}
        last_var = ''
        for line in configfile:
            #Stop before code
            if '###' in line:
                break
            #Get name of variable
            if line[0:2] == '__':
                last_var = line.split()[0]
            comment = ''
            #Find only in-line comments
            if not line [0:1] == '#':
                for word in line.split():
                    #If the line contains a comment
                    if word.startswith('#') or not comment == '':
                        comment = comment + word + ' '
                #Add comment to dict
                if not comment == '':
                    comments[last_var] = comment
        #Create empty file string
        tmp = ''
        value = ''
        configfile.seek(0)
        for line in configfile:
            #Variable lines
            if line[0:2] == '__':
                #Convert variable value into string
                variable = line.split()[0]
                #Get comment
                try:
                    comment = comments[variable]
                except:
                    comment = False
                #If the variable is a string
                if isinstance(eval(variable), str):
                    #Put quotes arround it
                    value = "'''" + str(eval(variable)) + "'''"
                    #Add the comment, if any
                    if comment:
                        line_length = len(value) + 24
                        value += ' ' * max(52 - line_length, 1)
                        value += comment
                else:
                    #If the variable is an enumerable, insert line breaks
                    string = str(eval(variable)).replace(',', 
                                                ',\n' + (' ' * 25))
                    #If the variable is an enumerable
                    if ',' in string:
                        value =''
                        last_word = ''
                        depth = 0
                        word_number = 0
                        #Cycle through elements
                        for word in string.split():
                            new_word = word
                            #Outdent if second, third... key of dict
                            if (word.endswith(':') and 
                                not word.startswith('{') and
                                last_word.endswith(',')):
                                depth -= 1
                            #Add indent spaces
                            if last_word[-1:] in [',', ':']:
                                new_word = ' ' * (depth * 5) + word
                            #Indent following elements to align with first
                            if not (word.startswith('[') or word.startswith('{')):
                                new_word = ' ' + new_word
                            #Elements other than last
                            if word.endswith(',') or word.endswith(':'):
                                #Add comment to first element
                                if comment and word_number == 0:
                                    line_length = len(word) + 24
                                    new_word += ' ' * max(52 - line_length, 1)
                                    new_word += comment
                                #Indent next line
                                new_word += '\n' + (' ' * 24)
                            else:
                                #Add comment to first element
                                if comment and word_number == 0:
                                    line_length = len(word) + 24
                                    new_word += ' ' * max(52 - line_length, 1)
                                    new_word += comment
                            #Indent next line if key of dict
                            if word.endswith(':'):
                                depth += 1
                            #Add the word to the variable value
                            value += new_word
                            word_number += 1
                            last_word = word
                    else:
                        value = string
                        #Add comment
                        if comment:
                            line_length = len(value) + 24
                            value += ' ' * max(52 - line_length, 1)
                            value += comment
                #If the variable's current value would be unable to be imported,
                #instead write it (and any following lines, if list or
                #dictionary) as-is and add to list.
                try:
                    eval(value)
                except SyntaxError:
                    unwriteable.append(line.split()[0])
                    #Add line as-is
                    tmp += line
                    variable = ''
                else:
                    #Add the variable name
                    tmp += (line[0:24])
                    #Add the variable value
                    tmp += value
                    #Add newline
                    tmp += '\n'
            #Following lines of lists and dicts.
            elif (value.endswith(']') or 
                  value.endswith('}') 
                 and
                 (line.endswith(',') or 
                  line.endswith(']') or 
                  line.endswith('}'))):
                pass
            #Non-variable lines
            else:
                #Add line as-is
                tmp += line
                variable = ''
    #Open config script, write over it, closing even with an exception.
    with open(self_path + 'x', 'w+') as configfile:
        configfile.write(tmp)
    #Return list of variables that could not be rewritten
    return unwriteable