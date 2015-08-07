# awap.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of awap.

"""

## Build Directory Layout
One awap configuration will be built in one build directory.
The layout will look something like this:

build
├── agents
│   └── TemperatureSensor
│       ├── class
│       │   └── de
│       │       └── rwth_aachen
│       │           └── awap
│       │               └── example
│       │                   └── agents
│       │                       └── TemperatureSensor.class
│       └── TemperatureSensor.jar
├── lib
│   ├── common
│   │   ├── class
│   │   └── generated
│   ├── jade
│   │   ├── class
│   │   └── generated
│   └── node
├── node
│   └── generated
└── ostfriesentee
    ├── app
    │   └── TemperatureSensor
    │       └── TemperatureSensor.di
    ├── lib
    │   ├── awap-common
    │   ├── awap-node
    │   ├── base
    │   ├── ostfriesentee
    │   └── util
    └── vm
"""

import os

def awap_method(env, configuration):
	""" This is a pseudo builder that generates a number of targets that
		can be executed in order to build different parts of awap.
	"""
	# load and validate awap configuration which in turn loads the communication
	agents = env.LoadAwapConfiguration(configuration)
	# load libcommon SConscript
	env.Alias('awap-common', env.SConscript(env['AWAP_LIB_COMMON'], exports = 'env'))
	env.Alias('awap-jade', env.SConscript(env['AWAP_LIB_JADE'], exports = 'env'))
	# build agents
	for agent in agents:
		env.Agent(**agent)

def generate(env):
	# define some paths
	env['AWAP_SCONS_TOOLS'] = os.path.dirname(os.path.abspath(__file__))
	env['AWAP_ROOT'] = os.path.join(env['AWAP_SCONS_TOOLS'], '..')
	env['AWAP_LIB_COMMON'] = os.path.join(env['AWAP_ROOT'], 'lib', 'common', 'SConscript')
	env['AWAP_LIB_JADE'] = os.path.join(env['AWAP_ROOT'], 'lib', 'jade', 'SConscript')
	env['AWAP_LIB_NODE'] = os.path.join(env['AWAP_ROOT'], 'lib', 'node', 'SConscript')

	# lists that need to be filled by the user
	env['AWAP_AGENT_PATH'] = []
	env['AWAP_COMMUNICATION_PATH'] = []

	# import terminal type to enable gcc/clang to print colored output
	# http://stackoverflow.com/questions/9922521/why-doesnt-clang-show-color-output-under-scons
	env['ENV']['TERM'] = os.environ['TERM']

	# copy path from os environment
	env['ENV']['PATH'] = os.environ['PATH']

	# determine build directory
	if not 'AWAP_BUILDPATH' in env:
		env['AWAP_BUILDPATH'] = os.path.join(env.Dir('.').abspath, 'build')
	# set ostfriesentee build path relative to awap build path
	env['OFT_BUILDPATH'] = os.path.join(env['AWAP_BUILDPATH'], 'ostfriesentee')

	# make sure to include all needed external tools
	env.Tool('default')
	env['toolpath'].append(os.path.join(env['AWAP_ROOT'], 'ext', 'ekiwi-scons-tools', 'tools'))
	env.Tool('template')
	# only works if indentifier is camelCase or CamelCase ....
	def filter_camelCase(identifier):
		return identifier[0].lower() + identifier[1:]
	env.AddTemplateFilter('camelCase', filter_camelCase)
	env['toolpath'].append(os.path.join(env['AWAP_ROOT'], 'ext', 'ostfriesentee', 'scons'))
	env.Tool('ostfriesentee')

	# load awap specific tools
	env.Tool('configuration')
	env.Tool('agent')

	# add pseudo builder to generate targets for a specific awap configuration
	env.AddMethod(awap_method, 'Awap')


def exists(env):
	return 1
