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

def generate(env):
	# define some paths
	env['AWAP_SCONS_TOOLS'] = os.path.dirname(os.path.abspath(__file__))
	env['AWAP_ROOT'] = os.path.abspath(os.path.join(env['AWAP_SCONS_TOOLS'], '..'))

	# import terminal type to enable gcc/clang to print colored output
	# http://stackoverflow.com/questions/9922521/why-doesnt-clang-show-color-output-under-scons
	env['ENV']['TERM'] = os.environ['TERM']

	# copy path from os environment
	env['ENV']['PATH'] = os.environ['PATH']

	# make sure to include all needed external tools
	env.Tool('default')
	env['toolpath'].append(os.path.join(env['AWAP_ROOT'], 'ext', 'ekiwi-scons-tools', 'tools'))
	# env.Tool('java2jar')
	env['toolpath'].append(os.path.join(env['AWAP_ROOT'], 'ext', 'ostfriesentee', 'scons'))
	env.Tool('ostfriesentee')

	# load awap specific tools
	env.Tool('communication')


def exists(env):
	return 1
