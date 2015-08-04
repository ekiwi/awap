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

def load_awap_confguration_method(env, configuration):
	print("LoadAwapConfiguration({})".format(configuration))


def generate(env):
	env.AddMethod(load_awap_confguration_method, 'LoadAwapConfiguration')

def exists(env):
	return 1
