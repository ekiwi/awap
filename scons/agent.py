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
import SCons

def agent_method(env, path, name):
	source_loc = (os.path.join(path, src) for src in ['src', 'java'])
	source = [src for src in source_loc if os.path.isdir(src)]
	# build ostfriesentee and regular jar
	agent_oft = env.OstfriesenteeApplication(name, source, OFT_LIBS=['base', 'util', 'awap-common'])
	jar_target = os.path.join(env['AWAP_AGENT_BUILDPATH'], name, name + '.jar')
	env_java = env.Clone()
	env_java.AppendUnique(JAVACLASSPATH=env['AWAP_LIB_COMMON_JAR'])
	agent_jar = env_java.JavaToJar(jar_target, source)
	env.Alias(name + '.oft', agent_oft)
	env.Alias(name + '.size', env.ShowSize(agent_oft))
	env.Alias(name + '.jar', agent_jar)
	return(agent_oft, agent_jar)

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

def agent_from_di_action(target, source, env):
	if 'AWAP_AGENT_FORMAT_COMPRESS' in env and env['AWAP_AGENT_FORMAT_COMPRESS']:
		env['AWAP_HUFFMAN_ENCODER'].compress_file(
			input_filename  = source[0].path,
			output_filename = target[0].path,
			prepend_input_size = True)
	else:
		env.Execute(SCons.Script.Copy(target[0].path, source[0].path))

def agent_from_di_emitter(target, source, env):
	if 'AWAP_AGENT_FORMAT_COMPRESS' in env and env['AWAP_AGENT_FORMAT_COMPRESS']:
		env.Depends(target, SCons.Node.Python.Value(
			env['AWAP_AGENT_FORMAT_COMPRESSSION_CODE']))
	return target, source

def agent_from_di_string(target, source, env):
	return "Agent: '{}'".format(str(target[0]))

def agent_c_array_method(env, target, agent_name):
	di = env['AWAP_AGENTS_DI'][agent_name]
	awap_agent = di + '.awap'
	return env.CArray(target, env.AgentFromDi(awap_agent, di))

def generate(env):
	# load configuration validator
	agent_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'agent.xsd')
	env['AWAP_AGENT_XSD'] = ET.XMLSchema(ET.parse(agent_xsd))

	env['AWAP_AGENT_BUILDPATH'] = os.path.join(env['AWAP_BUILDPATH'], 'agents')
	# public methods
	env.AddMethod(load_agent_method, 'LoadAgent')
	env.AddMethod(agent_method, 'Agent')
	env.AddMethod(agent_c_array_method, 'AgentCArray')

	# AgentFromDi builder used internaly in the AgentCArray pseudo builder
	agent_from_di_builder = SCons.Builder.Builder(
		action = env.Action(agent_from_di_action, agent_from_di_string),
		emitter = agent_from_di_emitter,
		src_suffix = '.di',
		single_source = True,
		target_factory = SCons.Node.FS.File,
		source_factory = SCons.Node.FS.File)
	env.Append(BUILDERS = { 'AgentFromDi': agent_from_di_builder })

def exists(env):
	return 1
