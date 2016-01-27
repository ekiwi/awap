# configuration.py
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

def load_awap_confguration_method(env, configuration, load_services_only=False):
	# open xml file
	tree = ET.parse(configuration)
	root = tree.getroot()
	# validate
	env['AWAP_CONFIGURATION_XSD'].assertValid(tree)
	# keep track of enums and services, that are required for this configuration
	env['AWAP_SERVICE_NAMES'] = []
	enum_names = []

	load_service_configuration(env, root)
	# TODO: enums
	if not load_services_only:
		agents = load_agents_configuration(env, root)
		load_agent_file_format_configuration(env, root, os.path.dirname(configuration))
	else:
		agents = []
	# at the end of this method, the communication has to be complete!
	pp = env['AWAP_COMMUNICATION_PARSER']
	env['AWAP_COMMUNICATION_DICT'] = pp.get_dict(env['AWAP_SERVICE_NAMES'], enum_names)

	return agents

def load_service_configuration(env, root):
	# parse
	services = root.find("services")
	max_id = int(services.get('max-id'))
	# a list that contains all services that were loaded
	for serv_node in services:
		service = load_service(env, serv_node.get('module'), serv_node.get('name'))
		service.id = int(serv_node.get('id'))
		full_name = "{}.{}".format(service.module.name, service.name)
		env['AWAP_SERVICE_NAMES'].append(full_name)

def load_agents_configuration(env, root):
	if root.find("agents") is not None:
		agents = [env.LoadAgent(agent.get("name")) for agent in root.find("agents")]
	else:
		agents = []
	return agents

def load_agent_file_format_configuration(env, root, configuration_path):
	env['AWAP_AGENT_FORMAT_COMPRESS'] = False
	if root.find("agent-format") is not None:
		comp = root.find("agent-format").find("compression")
		if comp is not None:
			env['AWAP_AGENT_FORMAT_COMPRESS'] = True
			symbols = [x.text for x in comp.findall('symbol')]
			symbol_src = [x.text for x in comp.findall('symbol-source')]
			symbol_files = [os.path.join(configuration_path, src) for src in symbol_src]
			generate_huffman_code(env, symbols, symbol_files)

def generate_huffman_code(env, symbols, symbol_files):
	from huffman import HuffmanCode, HuffmanEncoder
	hc = HuffmanCode()
	for symbol in symbols:
		hc.add_symbol(symbol)
	# this is somewhat inefficient, as file are loaded every time
	# one could move this into a scons builder, but I rally need to
	# get done with my thesis
	for src in symbol_files:
		hc.count_symbols_in_file(src)
	hc.generate()
	env['AWAP_HUFFMAN_ENCODER'] = HuffmanEncoder(hc)
	env['AWAP_AGENT_FORMAT_COMPRESSSION_CODE'] = hc.to_dict()

def get_communication_dict_method(env):
	""" returns a dictionary containing all communication elements
	    needed for the loaded configuration
	"""
	return env['AWAP_COMMUNICATION_DICT']

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

	# public methods
	env.AddMethod(load_awap_confguration_method, 'LoadAwapConfiguration')
	env.AddMethod(get_communication_dict_method, 'GetCommunicationDict')

def exists(env):
	return 1
