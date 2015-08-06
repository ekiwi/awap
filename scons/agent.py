# agent.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of awap.

"""
This scos tool is responsible for parsing agent configurations,
validating them and then telling scons how to build a specific agent.

Agents will be found in env['AWAP_AGENT_PATH']
"""

import os
import lxml.etree as ET

def agent_method(env, path, name):
	print("Agent({}, {})".format(path, name))

def load_agent_method(env, name):
	# search for {{ agent_name }}/agent.xml in agent path
	tree = None
	for path in env['AWAP_AGENT_PATH']:
		agent_path = os.path.join(path, name)
		filename = os.path.join(agent_path, 'agent.xml')
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
	# agent was successfuly validated!
	return { 'name': name, 'path': agent_path }


def generate(env):
	# load configuration validator
	agent_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'agent.xsd')
	env['AWAP_AGENT_XSD'] = ET.XMLSchema(ET.parse(agent_xsd))

	# public methods
	env.AddMethod(load_agent_method, 'LoadAgent')
	env.AddMethod(agent_method, 'Agent')

def exists(env):
	return 1
