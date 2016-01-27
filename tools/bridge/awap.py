#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# awap.py

import struct, os, sys
import lxml.etree as ET


class Awap():

	@staticmethod
	def load_xml(communication_path, configuration_file):
		awap_root = os.path.join(os.path.realpath(__file__), '..', '..', '..')
		env = { 'AWAP_ROOT': awap_root }
		env['AWAP_SCONS_TOOLS'] = os.path.abspath(os.path.join(awap_root, 'scons'))
		env['AWAP_COMMUNICATION_PATH'] = [communication_path]
		# load one global communication parser
		tools_path = os.path.join(env['AWAP_ROOT'], 'tools')
		sys.path.append(os.path.abspath(tools_path))
		from communication import CommunicationParser
		env['AWAP_COMMUNICATION_PARSER'] = CommunicationParser()
		# load configuration validators
		configuration_xsd = os.path.join(env['AWAP_SCONS_TOOLS'], 'configuration.xsd')
		env['AWAP_CONFIGURATION_XSD'] = ET.XMLSchema(ET.parse(configuration_xsd))

		# HACK: load scon tool
		sys.path.append(env['AWAP_SCONS_TOOLS'])
		from configuration import load_awap_confguration_method

		load_awap_confguration_method(env, configuration_file)

		print(env['AWAP_COMMUNICATION_DICT'])


	@staticmethod
	def message_to_dict(msg):
		assert(isinstance(msg, bytes))
		assert(len(msg) > 2)

		dd = {}
		dd['IsBroadcast'] = bool(msg[0] & (1<<7))
		dd['DestinationAgent'] = (msg[0] >> 3) & 0x7
		dd['SourceAgent'] = msg[0] & 0x7
		dd['ServiceType'] = msg[1]
		dd['MessageId']   = msg[2]

		# TODO: parse message specific fields

		return dd

	@staticmethod
	def message_to_bin(msg):
		assert(isinstance(msg, dict))

		bb0  = dd['SourceAgent'] & 0x7
		bb0 |= (dd['DestinationAgent'] & 0x7) << 3
		if dd['IsBroadcast']: bb0 |= (1<<7)

		bb  = struct.pack("B", bb0)
		bb += struct.pack("B", dd['ServiceType'])
		bb += struct.pack("B", dd['MessageId'])

		# TODO: write message specific part

		return bb

	@staticmethod
	def service_desc_to_dict(desc):
		assert(isinstance(desc, bytes))
		return {}

	@staticmethod
	def service_desc_to_bin(desc):
		assert(isinstance(desc, dict))
		return b'\x00'


import unittest

class Tester(unittest.TestCase):

	def test_RequestTemperatureMessage(self):
		msg_bin = b'\x33'


if __name__ == "__main__":
	path = os.path.abspath(os.path.join('..', '..', 'lib', 'mote', 'unittest', 'communication'))
	conf = os.path.abspath(os.path.join('..', '..', 'lib', 'mote', 'unittest', 'configuration.xml'))
	Awap.load_xml(path, conf)
	unittest.main()
