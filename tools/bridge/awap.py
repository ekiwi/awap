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

		services = env['AWAP_COMMUNICATION_DICT']['services']
		Awap.ServiceById = {service['id']: service for service in services}
		Awap.ServiceByName = {service['name']: service for service in services}
		Awap.MessagesById   = {serv['id']: { msg['id']: msg for msg in serv['messages'] } for serv in services}
		Awap.MessagesByName = {serv['name']: { msg['name']: msg for msg in serv['messages'] } for serv in services}
		enums = env['AWAP_COMMUNICATION_DICT']['enums']
		Awap.EnumToString = {enum['enum_name']: { elem['id']: elem['name'] for elem in enum['elements'] } for enum in enums}
		Awap.EnumToInt    = {enum['enum_name']: { elem['name']: elem['id'] for elem in enum['elements'] } for enum in enums}

	@staticmethod
	def field_to_dict(dd, field, msg, ii):
		if field['is_bool']:
			fmt = '?'
		elif field['is_enum']:
			fmt = 'B'
		else:
			fmt = {1: 'b', 2: 'h', 4: 'i'}[field['size']]
		old_ii = ii
		ii += struct.calcsize(fmt)
		value = struct.unpack(fmt, msg[old_ii:ii])[0]
		if field['is_enum']:
			dd[field['name']] = Awap.EnumToString[field['enum_name']][value]
		else:
			dd[field['name']] = value
		return ii

	@staticmethod
	def message_to_dict(msg):
		assert(isinstance(msg, bytes))
		assert(len(msg) > 2)

		dd = {}
		# read header
		dd['IsBroadcast'] = bool(msg[0] & (1<<7))
		dd['DestinationAgent'] = (msg[0] >> 3) & 0x7
		dd['SourceAgent'] = msg[0] & 0x7
		service_id = msg[1]
		message_id = msg[2]

		# look up information from xml
		service_name = Awap.ServiceById[service_id]['name']
		msg_type = Awap.MessagesById[service_id][message_id]

		# parse message specific fields
		content = {'service' : service_name, 'message': msg_type['name']}
		ii = 3
		for field in msg_type['fields']:
			ii = Awap.field_to_dict(content, field, msg, ii)
		dd['Content'] = content

		return dd

	@staticmethod
	def message_to_bin(dd):
		assert(isinstance(dd, dict))

		bb0  = dd['SourceAgent'] & 0x7
		bb0 |= (dd['DestinationAgent'] & 0x7) << 3
		if dd['IsBroadcast']: bb0 |= (1<<7)
		bb  = struct.pack("B", bb0)

		content = dd['Content']
		service_id = Awap.ServiceByName[content['service']]['id']
		msg_type = Awap.MessagesByName[content['service']][content['message']]
		bb += struct.pack("B", service_id)
		bb += struct.pack("B", msg_type['id'])

		# parse message specific fields
		for field in msg_type['fields']:
			value = content[field['name']]
			if field['is_bool']:
				fmt = '?'
			elif field['is_enum']:
				value = Awap.EnumToInt[field['enum_name']][value]
				fmt = 'B'
			else:
				fmt = {1: 'b', 2: 'h', 4: 'i'}[field['size']]
			bb += struct.pack(fmt, value)

		return bb

	@staticmethod
	def service_desc_to_dict(service_id, desc):
		assert(isinstance(desc, bytes))
		assert(isinstance(service_id, int))

		service = Awap.ServiceById[service_id]
		dd = { 'service': service['name'] }
		fields = service['properties']['fields']

		mask = desc[0]
		ii = 1
		for mask_index, field in zip(range(0,len(fields)), fields):
			if mask & (1 << (7-mask_index)):
				ii = Awap.field_to_dict(dd, field, desc, ii)

		return dd

	@staticmethod
	def service_desc_to_bin(desc):
		assert(isinstance(desc, dict))
		return b'\x00'


import unittest

class Tester(unittest.TestCase):

	def test_SimpleIntMessage(self):
		# Broadcast: false, SourceAgent: 2, DestinationAgent: 3
		msg_dd = Awap.message_to_dict(b'\x1a\x00\x00\xaa\xaa\xaa\x00')
		self.assertEqual(msg_dd['IsBroadcast'], False)
		self.assertEqual(msg_dd['SourceAgent'], 2)
		self.assertEqual(msg_dd['DestinationAgent'], 3)
		# not used for simplicity
		# self.assertEqual(msg_dd['ServiceId'], 0)
		# self.assertEqual(msg_dd['MessageId'], 0)
		# self.assertEqual(msg_dd['ServiceName'], "MessageTestService")
		# self.assertEqual(msg_dd['MessageName'], "SimpleIntMessage")
		self.assertEqual(msg_dd['Content']['service'], "MessageTestService")
		self.assertEqual(msg_dd['Content']['message'], "SimpleIntMessage")
		self.assertEqual(msg_dd['Content']['int_value'], 0xaaaaaa)
		msg_bin = Awap.message_to_bin(msg_dd)
		self.assertEqual(msg_bin, b'\x1a\x00\x00\xaa\xaa\xaa\x00')

	def test_EnergySupplyServiceDescription(self):
		# the EnergySupplyService (id=7) has three different enum properties:
		# Building, SupplyCircuit, Room
		# 1.) Building=SemiTemp, Room=R2
		desc_dd = Awap.service_desc_to_dict(7, b'\xa0\x02\x01')
		self.assertEqual(desc_dd['service'], "EnergySupplyService")
		self.assertEqual(desc_dd['building'], "SemiTemp")
		self.assertFalse('supplyCircuit' in desc_dd)
		self.assertEqual(desc_dd['room'], "R2")

if __name__ == "__main__":
	path = os.path.abspath(os.path.join('..', '..', 'lib', 'mote', 'unittest', 'communication'))
	conf = os.path.abspath(os.path.join('..', '..', 'lib', 'mote', 'unittest', 'configuration.xml'))
	Awap.load_xml(path, conf)
	# print(Awap.Messages)
	unittest.main()
