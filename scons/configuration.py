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

import os, math
import lxml.etree as ET

def load_awap_confguration_method(env, configuration):
	print("LoadAwapConfiguration({})".format(configuration))
	# open xml file
	tree = ET.parse(configuration)
	root = tree.getroot()
	# validate
	env['AWAP_CONFIGURATION_XSD'].assertValid(tree)
	# parse
	agents = root.find("agents")
	for agent in agents:
		load_awap_agent(env, agent.get("name"))

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


def generate(env):
	configuration_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'configuration.xsd')
	env['AWAP_CONFIGURATION_XSD'] = ET.XMLSchema(ET.parse(configuration_xsd))
	agent_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'agent.xsd')
	env['AWAP_AGENT_XSD'] = ET.XMLSchema(ET.parse(agent_xsd))
	env.AddMethod(load_awap_confguration_method, 'LoadAwapConfiguration')

def exists(env):
	return 1