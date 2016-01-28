#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

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
if __name__ == "__main__":
	import aclparser
else:
	from . import aclparser

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

	def __init__(self, name=None, addresses=None):
		if addresses is None:
			addresses = []
		elif not isinstance(addresses, list):
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

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return hash((self.name, "".join(self.addresses)))

	def __eq__(self, other):
		return (self.name, self.addresses) == (other.name, other.addresses)

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

class ACLEnvelope(object):
	"""
	See http://www.fipa.org/specs/fipa00085/SC00085J.html
	"""
	def __init__(self, sender, receiver, content, representation='fipa.acl.rep.string.std'):
		self.sender = sender
		self.receiver = receiver
		self.acl_representation = representation
		self._content = content.strip()
		self._msg = None

	@classmethod
	def from_message(cls, acl_msg):
		env = ACLEnvelope(
			sender = [acl_msg.sender],
			receiver = acl_msg.receiver,
			content = str(acl_msg),
			representation='fipa.acl.rep.string.std')
		return env

	@classmethod
	def from_mtp(cls, envelope, content):
		receiver = []
		sender = []
		length = 0
		representation=None
		root = ET.fromstring(envelope.strip())
		if root.tag != 'envelope':
			raise Exception("Invalid xml. Expected root tag to be <envelope>")
		# TODO: check more than one <params> tag
		params = root.find('params')
		for identifier in params.find('to'):
			receiver.append(AgentIdentifier.from_xml(identifier))
		for identifier in params.find('from'):
			sender.append(AgentIdentifier.from_xml(identifier))
		representation = params.find('acl-representation').text
		length = int(params.find('payload-length').text)
		if len(content) != length:
			print("WARN: in ACLEnvelope.from_mtp: length ({}) does not match len(content) ({})".format(length, len(content)))
		return ACLEnvelope(sender, receiver, content, representation)

	@property
	def msg(self):
		if self._msg is None:
			self._msg = ACLMessage.from_mtp(self.content)
		return self._msg

	@property
	def content(self):
		return self._content

	@content.setter
	def content(self, value):
		value = value.strip()
		if self._content != value:
			self._msg = None
			self._content = value

	def xml(self):
		root = ET.Element('envelope')
		param = ET.SubElement(root, 'params')
		param.set('index', '1')
		to = ET.SubElement(param, 'to')
		for receiver in self.receiver:
			to.append(receiver.xml())
		fro = ET.SubElement(param, 'from')
		for sender in self.sender:
			fro.append(sender.xml())
		# TODO: what is this for? do we not intent to send our message to
		#       all receivers?
		intended = ET.SubElement(param, 'intended-receiver')
		for receiver in self.receiver:
			intended.append(receiver.xml())
		ET.SubElement(param, 'payload-length').text = str(len(self.content))
		# currently string representation is hard coded
		ET.SubElement(param, 'acl-representation').text = self.acl_representation
		now = datetime.utcnow()
		ts = "{0}{1:03d}".format(now.strftime("%Y%m%dZ%H%M%S"), int(now.microsecond / 1000))
		ET.SubElement(param, 'date').text = ts
		return root

	def xml_string(self):
		return ET.tostring(self.xml(), encoding='unicode', method='xml')

class ACLMessage(object):
	"""
		See http://www.fipa.org/specs/fipa00070/SC00070I.html
	"""
	ACLParserSingleton = None

	def __init__(self, performative=None):
		if ACLMessage.ACLParserSingleton is None:
			ACLMessage.ACLParserSingleton = aclparser.ACLParser()
		self.parser = ACLMessage.ACLParserSingleton
		self.mime_type = "application/text"
		if isinstance(performative, str):
			performative = getattr(Performative, performative)
		self.performative = performative
		for param in self.parser.MessageParameterNames:
			if param in ['receiver', 'reply-to']:
				setattr(self, param.replace('-', '_'), [])
			else:
				setattr(self, param.replace('-', '_'), None)

	@classmethod
	def from_mtp(cls, msg):
		a = ACLMessage()
		a.parse_string_message(msg)
		return a

	def parse_string_message(self, message):
		msg = self.parser.parse_message(message)[0]
		self.performative = Performative[msg['performative'].replace('-','_')]
		for param in self.parser.MessageParameterNames:
			if param in msg:
				if param == 'sender':
					self.sender = AgentIdentifier(msg['sender']['name'], msg['sender']['addresses'])
				elif param == 'receiver':
					self.receiver = [
						AgentIdentifier(rr['name'], rr['addresses'])
						for rr in msg['receiver']]
				else:
					setattr(self, param.replace('-', '_'), msg[param])

	def __str__(self):
		# make sure sender is not a list
		assert isinstance(self.sender, AgentIdentifier)
		s = '(' + self.performative.name + ' '
		parameters = vars(self)
		for param in self.parser.MessageParameterNames:
			key = param.replace('-', '_')
			if key in parameters and parameters[key]:
				s += ' :' + param + ' '
				s += self._to_acl_string(parameters[key])
		s += ')'
		return s

	def _to_acl_string(self, value):
		if isinstance(value, list):
			s  = '(set '
			s += ' '.join([self._to_acl_string(v) for v in value])
			s += ' )'
			return s
		elif isinstance(value, str):
			# test if this is a Word or a StringLiteral
			return value if self.parser.is_Word(value) else self._make_string_literal(value)
		else:
			return str(value)

	def _make_string_literal(self, value):
		return '"{}"'.format(value.replace('"', '\\"'))

class TestACLMessageParsing(unittest.TestCase):
	def setUp(self):
		self.acl = ACLMessage()
		self.test_envelope = ["""

<?xml version="1.0"?>
<envelope><params index="1"><to><agent-identifier><name>test</name><addresses><url>http://localhost:9000</url></addresses></agent-identifier></to><from><agent-identifier><name>rma@192.168.122.1:1099/JADE</name><addresses><url>http://130-000.eduroam.rwth-aachen.de:7778/acc</url></addresses></agent-identifier></from><acl-representation>fipa.acl.rep.string.std</acl-representation><payload-length>488</payload-length><date>20150701Z143941567</date><intended-receiver><agent-identifier><name>test</name><addresses><url>http://localhost:9000</url></addresses></agent-identifier></intended-receiver></params></envelope>

"""]
		test_msg0 = ACLMessage(Performative.REQUEST)
		test_msg0.sender = AgentIdentifier("rma@192.168.122.1:1099/JADE", "http://130-000.eduroam.rwth-aachen.de:7778/acc")
		test_msg0.receiver = [AgentIdentifier("test", "http://localhost:9000")]
		test_msg0.content = "((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))"
		test_msg0.tlanguage = "fipa-sl0"
		test_msg0.ontology = "FIPA-Agent-Management"
		test_msg0.protocol = "fipa-request"
		test_msg0.conversation_id = "C1438784720_1435754381566"
		test_msg0_str = """


(REQUEST
 :sender  ( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ))
 :receiver  (set ( agent-identifier :name test  :addresses (sequence http://localhost:9000 )) )
 :content  "((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))" 
 :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request
 :conversation-id  C1438784720_1435754381566 )

"""
		test_msg1 = ACLMessage(Performative.INFORM)
		test_msg1.sender     = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
		test_msg1.receiver  += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
		test_msg1.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name "192.168.122.1:1099/JADE" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
		test_msg1.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
		test_msg1.language = "fipa-sl0"
		test_msg1.ontology = "FIPA-Agent-Management"
		test_msg1.protocol = "fipa-request"
		test_msg1_str = """

(INFORM
 :sender  ( agent-identifier :name ams@192.168.122.1:1099/JADE  :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc ))
 :receiver  (set ( agent-identifier :name rma@192.168.122.1:5000/JADE  :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:57727/acc )) )
 :content  "((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name \\"192.168.122.1:1099/JADE\\" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))" 
 :reply-with  rma@192.168.122.1:5000/JADE1435662093800  :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request
 :conversation-id  C1575934033_1435662093795 )

"""
		self.test_msg = [(test_msg0, test_msg0_str), (test_msg1, test_msg1_str)]

	def _helper_compare_msg(self, msg0, msg1):
		self.assertEqual(msg0.performative, msg1.performative)
		self.assertEqual(msg0.sender.name, msg0.sender.name)
		self.assertEqual(msg0.sender.addresses[0], msg0.sender.addresses[0])
		self.assertEqual(msg0.receiver[0].name, msg0.receiver[0].name)
		self.assertEqual(msg0.receiver[0].addresses[0], msg0.receiver[0].addresses[0])
		self.assertEqual(msg0.content, msg0.content)
		self.assertEqual(msg0.language, msg0.language)
		self.assertEqual(msg0.ontology, msg0.ontology)
		self.assertEqual(msg0.protocol, msg0.protocol)
		self.assertEqual(msg0.conversation_id, msg0.conversation_id)


	def test_msg_from_mtp(self):
		for test in self.test_msg:
			self._helper_compare_msg(ACLMessage.from_mtp(test[1]), test[0])

	def test_msg_to_string(self):
		for test in self.test_msg:
			original_msg = test[0]
			msg_str = str(original_msg)
			msg = ACLMessage.from_mtp(msg_str)
			self._helper_compare_msg(msg, original_msg)

	def test_envelope_from_mtp(self):
		env = ACLEnvelope.from_mtp(self.test_envelope[0], self.test_msg[0][1])
		self.assertEqual(env.receiver[0].name, "test")
		self.assertEqual(env.receiver[0].addresses[0], "http://localhost:9000")
		self.assertEqual(env.sender[0].name, "rma@192.168.122.1:1099/JADE")
		self.assertEqual(env.sender[0].addresses[0], "http://130-000.eduroam.rwth-aachen.de:7778/acc")
		self.assertEqual(env.content, self.test_msg[0][1].strip())
		self._helper_compare_msg(env.msg, self.test_msg[0][0])

	def test_ACLMessage_performative_from_string(self):
		msg = ACLMessage("INFORM")
		self.assertEqual(msg.performative, Performative.INFORM)
		msg = ACLMessage("REQUEST")
		self.assertEqual(msg.performative, Performative.REQUEST)

if __name__ == "__main__":
	unittest.main()
