# awap.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of awap.

"""
This scos tool is responsible for parsing and evaluationg an awap
configuration as well as associated agent files.

Agents will be found in env['AWAP_AGENT_PATH']
Communication files will be found in env['AWAP_COMMUNICATION_PATH']
"""

import os, math, sys
import lxml.etree as ET

def load_awap_confguration_method(env, configuration):
	print("LoadAwapConfiguration({})".format(configuration))
	# open xml file
	tree = ET.parse(configuration)
	root = tree.getroot()
	# validate
	env['AWAP_CONFIGURATION_XSD'].assertValid(tree)
	# keep track of enums and services, that are required for this configuration
	env['AWAP_SERVICE_NAMES'] = []
	enum_names = []
	# parse
	services = root.find("services")
	max_id = int(services.get('max-id'))
	# a list that contains all services that were loaded
	for serv_node in services:
		service = load_service(env, serv_node.get('module'), serv_node.get('name'))
		service.id = int(serv_node.get('id'))
		full_name = "{}.{}".format(service.module.name, service.name)
		env['AWAP_SERVICE_NAMES'].append(full_name)
	# TODO: enums
	agents = root.find("agents")
	for agent in agents:
		load_awap_agent(env, agent.get("name"))
	# at the end of this method, the communication has to be complete!
	pp = env['AWAP_COMMUNICATION_PARSER']
	env['AWAP_COMMUNICATION_DICT'] = pp.get_dict(env['AWAP_SERVICE_NAMES'], enum_names)

def get_communication_dict_method(env):
	""" returns a dictionary containing all communication elements
	    needed for the loaded configuration
	"""
	return env['AWAP_COMMUNICATION_DICT']

def load_awap_agent(env, name):
	print("LoadAwapAgent({})".format(name))
	# search for {{ agent_name }}/agent.xml in agent path
	tree = None
	for path in env['AWAP_AGENT_PATH']:
		filename = os.path.join(path, name, 'agent.xml')
		try: tree = ET.parse(filename)
		except: continue
	# show error and exit if agent was not found (this is fatal)
	if tree is None:
		env.Error('Failed to find agent "{}" in path:\n{}'.format(
			name, '\n'.join(env['AWAP_AGENT_PATH'])))
		exit(1)
	root = tree.getroot()
	# validate
	env['AWAP_AGENT_XSD'].assertValid(tree)
	# make sure agent name matches
	if root.get('name') != name:
		env.Error('Name specified in "{}" ("{}") '.format(filename, root.get('name')) +
			' does not match directory name "{}"!'.format(name))
		exit(1)
	# make sure required services are available
	services = root.findall('service')
	for service in services:
		full_name = "{}.{}".format(service.get('module'), service.get('name'))
		if not full_name in env['AWAP_SERVICE_NAMES']:
			env.Error('Service "{}.{}"'.format(service.get('module'), service.get('name')) +
				' required for agent "{}" was not found.\n'.format(name) +
				'Did you load that service in your configuration xml file?')
			exit(1)
	# TODO: add agent to some sort of database...

def load_service(env, module, name):
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

def generate(env):
	# load one global communication parser
	tools_path = os.path.join(env['AWAP_ROOT'], 'tools')
	sys.path.append(tools_path)
	from communication import CommunicationParser
	env['AWAP_COMMUNICATION_PARSER'] = CommunicationParser()

	# load configuration validators
	configuration_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'configuration.xsd')
	env['AWAP_CONFIGURATION_XSD'] = ET.XMLSchema(ET.parse(configuration_xsd))
	agent_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'agent.xsd')
	env['AWAP_AGENT_XSD'] = ET.XMLSchema(ET.parse(agent_xsd))

	# public methods
	env.AddMethod(load_awap_confguration_method, 'LoadAwapConfiguration')
	env.AddMethod(get_communication_dict_method, 'GetCommunicationDict')

def exists(env):
	return 1
