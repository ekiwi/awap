# awap.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of awap.
#
#
"""
This scons tools uses the communication parser from awap/tools/communication
in order to parse communication xml and to generate code from it
"""

import os, sys

def load_service_method(env, module, name, id):
	""" Tries to load the service specified by name from the
	    AWAP_COMMUNICATION_PATH
	    If found, the service is added to the list of loaded services
	    and assigned the service_id specified.
	"""
	print('LoadService("{}", "{}", {})'.format(module, name, id))
	parser = env['AWAP_COMMUNICATION_PARSER']
	# make sure path is up to date
	parser.path = env['AWAP_COMMUNICATION_PATH']
	# make sure module is parsed
	parser.parse(module)

def is_service_loaded_method(env, module, name):
	""" Returns true if the service specified by name has been loaded
	"""
	return False

def generate(env):
	tools_path = os.path.join(env['AWAP_ROOT'], 'tools')
	sys.path.append(tools_path)
	from communication import CommunicationParser
	env['AWAP_COMMUNICATION_PARSER'] = CommunicationParser()
	env.AddMethod(load_service_method, 'LoadService')
	env.AddMethod(is_service_loaded_method, 'IsServiceLoaded')

def exists(env):
	return 1
