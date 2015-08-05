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

def load_service_method(env, module, name):
	""" Tries to load the service specified by name from the
	    AWAP_COMMUNICATION_PATH
	    If found, the service is returned
	"""
	parser = env['AWAP_COMMUNICATION_PARSER']
	# make sure path is up to date
	parser.path = env['AWAP_COMMUNICATION_PATH']
	# make sure module is parsed
	try: parser.parse(module)
	except Exception as ee:
		env.Error('Failed to parse module "{}":'.format(module))
		env.Error(ee)
		exit(1)
	# make sure service exists in module
	mod = parser.modules[module]
	if not name in mod.services:
		env.Error('Could not find service "{}" '.format(name) +
			'in module "{}" ("{}")'.format(mod.name, mod.filename))
		exit(1)
	# return service
	return mod.services[name]

def is_service_loaded_method(env, module, name):
	""" Returns true if the service specified by name has been loaded
	"""
	return False

def generate(env):
	# load one global communication parser
	tools_path = os.path.join(env['AWAP_ROOT'], 'tools')
	sys.path.append(tools_path)
	from communication import CommunicationParser
	env['AWAP_COMMUNICATION_PARSER'] = CommunicationParser()

	env.AddMethod(load_service_method, 'LoadService')
	env.AddMethod(is_service_loaded_method, 'IsServiceLoaded')

def exists(env):
	return 1
