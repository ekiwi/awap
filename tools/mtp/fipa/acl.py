#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# acl.py

"""
	This library provides an incomplete subset of the FIPA ACL
	Message Representation in String Specification (SC00070I)
	http://www.fipa.org/specs/fipa00070/SC00070I.html
	Ass well as the FIPA Agent Message Transport Envelope
	Representation in XML Specification
	http://www.fipa.org/specs/fipa00085/SC00085J.html
"""

from enum import Enum
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import unittest

class Performative(Enum):
	ACCEPT_PROPOSAL = 0
	AGREE = 1
	CANCEL = 2
	CFP = 3
	CONFIRM = 4
	DISCONFIRM = 5
	FAILURE = 6
	INFORM = 7
	INFORM_IF = 8
	INFORM_REF = 9
	NOT_UNDERSTOOD = 10
	PROPOSE = 11
	QUERY_IF = 12
	QUERY_REF = 13
	REFUSE = 14
	REJECT_PROPOSAL = 15
	REQUEST = 16
	REQUEST_WHEN = 17
	REQUEST_WHENEVER = 18
	SUBSCRIBE = 19
	PROXY = 20
	PROPAGATE = 21

class MessageParameterType(Enum):
	AgentIdentifier = 0
	AgentIdentifierSet = 1
	String = 2
	Expression = 3
	DateTime = 4

class AgentIdentifier(object):

	def __init__(self, name=None, addresses=[]):
		if not isinstance(addresses, list):
			addresses = [addresses]
		self.name = name
		self.addresses = addresses

	def __str__(self):
		s  = '( agent-identifier :name ' + self.name
		s += ' :addresses (sequence '
		for address in self.addresses:
			s += address + ' '
		s += '))'
		return s

	def isempty(self):
		return self.name is None

	def xml(self):
		root = ET.Element('agent-identifier')
		ET.SubElement(root, 'name').text = self.name
		addr = ET.SubElement(root, 'addresses')
		for address in self.addresses:
			ET.SubElement(addr, 'url').text = address
		return root

	@classmethod
	def from_xml(cls, root):
		ai = AgentIdentifier()
		if root.tag != "agent-identifier":
			raise Exception("XML parse Error: expected root to be <agent-identifier>, but got <{}>".format(root.tag))
		ai.name = root.find('name').text
		for url in root.find('addresses'):
			ai.addresses.append(url.text)
		return ai

class AgentIdentifierSet(list):
	def isempty(self):
		return len(self) == 0

class String(str):
	def isempty(self):
		return len(self) == 0

class Expression(str):
	def isempty(self):
		return len(self) == 0

class Word(str):
	def isempty(self):
		return len(self) == 0

class Time(str):
	def isempty(self):
		return len(self) == 0

class ACLMessage(object):
	"""
		See http://www.fipa.org/specs/fipa00070/SC00070I.html
	"""

	FIPA_PARAMETERS = {
		'sender':      MessageParameterType.AgentIdentifier,
		'receiver':    MessageParameterType.AgentIdentifierSet,
		'content':     MessageParameterType.String,
		'reply-with':  MessageParameterType.Expression,
		'reply-by':    MessageParameterType.DateTime,
		'in-reply-to': MessageParameterType.Expression,
		'reply-to':    MessageParameterType.AgentIdentifierSet,
		'language':    MessageParameterType.Expression,
		'ontology':    MessageParameterType.Expression,
		# should be word, but JADE apparently uses strings
		'protocol':    MessageParameterType.String,
		'conversation-id': MessageParameterType.Expression,
	}

	RE_WORD = re.compile(r'\s*(?P<word>[^\(\)#0-9-@ ][^\(\) ]*)')
	RE_DATETIME = re.compile(
		r'\s*(?P<sign>[\+-])?(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})' +
		r'(T|Z)(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})' +
		r'(?P<millisecond>\d{3})([a-zA-Z])?')
	RE_INTEGER = re.compile(r'\s*(?P<int>[\+-]?[0-9]+)')
	RE_STRINGLITERAL = re.compile(r'\s*"(?P<string>(([^"])|(\"))+)"')

	def __init__(self, performative=None):
		self.mime_type = "application/text"
		self.performative = performative
		for param_name, param_type in ACLMessage.FIPA_PARAMETERS.items():
			if param_type in [MessageParameterType.AgentIdentifierSet]:
				setattr(self, param_name.replace('-', '_'), [])
			else:
				setattr(self, param_name.replace('-', '_'), None)

	@classmethod
	def from_mtp(cls, envelope, msg):
		a = ACLMessage()
		a.parse_xml_envelope(envelope)
		a.parse_string_message(msg)
		return a

	def generate_envelope(self):
		"""
		See http://www.fipa.org/specs/fipa00085/SC00085J.html
		"""
		root = ET.Element('envelope')
		param = ET.SubElement(root, 'params')
		param.set('index', '1')
		to = ET.SubElement(param, 'to')
		for receiver in self.receiver:
			to.append(receiver.xml())
		ET.SubElement(param, 'from').append(self.sender.xml())
		# TODO: what is this for? do we not intent to send our message to
		#       all receivers?
		intended = ET.SubElement(param, 'intended-receiver')
		for receiver in self.receiver:
			intended.append(receiver.xml())
		# FIXME: this is a little bit inefficient, since we prob. generate the string twice
		ET.SubElement(param, 'payload-length').text = str(len(str(self)))
		# currently string representation is hard coded
		ET.SubElement(param, 'acl-representation').text = 'fipa.acl.rep.string.std'
		now = datetime.utcnow()
		ts = "{0}{1:03d}".format(now.strftime("%Y%m%dZ%H%M%S"), int(now.microsecond / 1000))
		ET.SubElement(param, 'date').text = ts
		return ET.tostring(root, encoding='unicode', method='xml')

	def parse_xml_envelope(self, envelope):
		root = ET.fromstring(envelope.strip())
		if root.tag != 'envelope':
			raise Exception("Invalid xml. Expected root tag to be <envelope>")
		for params in root:
			if params.tag != "params":
				raise Exception("Invalid xml. Expected only params tag to be in <envelope>")
			receiver = []
			for identifier in params.find('to'):
				receiver.append(AgentIdentifier.from_xml(identifier))
			sender = AgentIdentifier.from_xml(params.find('from')[0])
			representation = params.find('acl-representation').text
		if representation != 'fipa.acl.rep.string.std':
			raise Exception("Error: envelope specifies `{}`. Can only read fipa.acl.rep.string.std.".format(representation))

	def parse_string_message(self, message):
		# find performative
		performatives = '|'.join([p.name for p in Performative])
		m = re.search(r'\s*\((?P<perf>{})'.format(performatives), message)
		self.performative = Performative[m.group('perf')]
		# find parameters
		parameters = '|'.join([str(p) for p in ACLMessage.FIPA_PARAMETERS])
		re_param = re.compile(r'\s*:(?P<param>{}) '.format(parameters))
		pos = m.end(0)
		max_pos = len(message)
		while pos < max_pos:
			m = re_param.match(message, pos)
			pos = m.end(0)
			param = m.group('param')
			key = param.replace('-', '_')
			#if param_type in [MessageParameterType.AgentIdentifierSet]:
			#	print("TODO: implement")
			print(param)
			(value, pos) = self.parse_expression(message, pos)
			print(value)

	def parse_expression(self, message, pos):
		m = ACLMessage.RE_DATETIME.match(message, pos)
		if m:
			ts = datetime(
				int(m.group('year')),
				int(m.group('month')),
				int(m.group('day')),
				int(m.group('hour')),
				int(m.group('minute')),
				int(m.group('second')),
				int(m.group('millisecond')) * 1000)
			return (ts, m.end(0))
		m = ACLMessage.RE_STRINGLITERAL.match(message, pos)
		if m:
			return (m.group('string'), m.end(0))
		m = ACLMessage.RE_INTEGER.match(message, pos)
		if m:
			return (int(m.group('int')), m.end(0))
		m = ACLMessage.RE_WORD.match(message, pos)
		if m:
			return (m.group('word'), m.end(0))
		print("Unkown expression @ pos={}:\n{}".format(pos, message[pos:]))

	def __str__(self):
		s = '(' + self.performative.name + ' '
		parameters = vars(self)
		for pp in ACLMessage.FIPA_PARAMETERS:
			key = pp.replace('-', '_')
			if key in parameters and parameters[key]:
				s += ' :' + pp + ' '
				s += ACLMessage._to_acl_string(parameters[key])
		s += ')'
		return s

	def _to_acl_string(value):
		if isinstance(value, list):
			s  = '(set '
			s += ' '.join([ACLMessage._to_acl_string(v) for v in value])
			s += ' )'
			return s
		else:
			return str(value)

class TestACLMessageParsing(unittest.TestCase):
	def setUp(self):
		self.acl = ACLMessage()

	def test_datetime(self):
		(ts, pos) = self.acl.parse_expression(" +20150701T143941567Z ", 0)
		print(ts)
		self.assertEqual(pos, 21)
		self.assertEqual(ts.year, 2015)
		self.assertEqual(ts.month, 7)
		self.assertEqual(ts.day, 1)
		self.assertEqual(ts.hour, 14)
		self.assertEqual(ts.minute, 39)
		self.assertEqual(ts.second, 41)
		self.assertEqual(ts.microsecond, 567 * 1000)

	def test_word(self):
		(word, pos) = self.acl.parse_expression(" word", 0)
		self.assertEqual(pos, 5)
		self.assertEqual(word, "word")
		(word, pos) = self.acl.parse_expression(" w(ord", 0)
		self.assertNotEqual(word, "w(ord")

	def test_string_literal(self):
		(string, pos) = self.acl.parse_expression(' "string"', 0)
		self.assertEqual(pos, 9)
		self.assertEqual(string, "string")
		(string, pos) = self.acl.parse_expression(' "str\\"ing"', 0)
		self.assertEqual(string, 'str\\"ing')

if __name__ == "__main__":
	unittest.main()
#	acl_msg = ACLMessage(Performative.INFORM)
#	acl_msg.sender     = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
#	acl_msg.receiver  += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
#	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name \"\\"192.168.122.1:1099/JADE\\"\" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
#	acl_msg.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
#	acl_msg.language = "fipa-sl0"
#	acl_msg.ontology = "FIPA-Agent-Management"
#	acl_msg.protocol = "fipa-request"

#	print(acl_msg)

#	print(acl_msg.generate_envelope())

#	print(ET.dump(acl_msg.sender.xml()))

#	envelope = """

#<?xml version="1.0"?>
#<envelope><params index="1"><to><agent-identifier><name>test</name><addresses><url>http://localhost:9000</url></addresses></agent-identifier></to><from><agent-identifier><name>rma@192.168.122.1:1099/JADE</name><addresses><url>http://130-000.eduroam.rwth-aachen.de:7778/acc</url></addresses></agent-identifier></from><acl-representation>fipa.acl.rep.string.std</acl-representation><payload-length>483</payload-length><date>20150701Z143941567</date><intended-receiver><agent-identifier><name>test</name><addresses><url>http://localhost:9000</url></addresses></agent-identifier></intended-receiver></params></envelope>

#"""

#	msg = """


#(REQUEST
# :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request
# :sender  ( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ))
# :receiver  (set ( agent-identifier :name test  :addresses (sequence http://localhost:9000 )) )
# :content  "((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))" 
# :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request
# :conversation-id  C1438784720_1435754381566 )

#"""
#	print("-----------------------------")
#	print("Testing from_mtp")

#	acl_msg = ACLMessage.from_mtp(envelope, msg)
#	print(acl_msg)
