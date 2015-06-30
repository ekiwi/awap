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

class AgentIdentifier(object):
	def __init__(self, name, addresses=[""]):
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

	def xml(self):
		root = ET.Element('agent-identifier')
		ET.SubElement(root, 'name').text = self.name
		addr = ET.SubElement(root, 'addresses')
		for address in self.addresses:
			ET.SubElement(addr, 'url').text = address
		return root

class ACLMessage(object):
	"""
		See http://www.fipa.org/specs/fipa00070/SC00070I.html
	"""

	def __init__(self, performative):
		self.mime_type = "application/text"
		self.performative = performative
		self.sender = None
		self.receivers = []
		self.content = None
		self.reply_with = None
		self.language = None
		self.ontology = None
		self.protocol = None

	def generateEnvelope(self):
		"""
		See http://www.fipa.org/specs/fipa00085/SC00085J.html
		"""
		root = ET.Element('envelope')
		param = ET.SubElement(root, 'params')
		param.set('index', '1')
		to = ET.SubElement(param, 'to')
		for receiver in self.receivers:
			to.append(receiver.xml())
		ET.SubElement(param, 'from').append(self.sender.xml())
		# TODO: what is this for? do we not intent to send our message to
		#       all receivers?
		intended = ET.SubElement(param, 'intended-receiver')
		for receiver in self.receivers:
			intended.append(receiver.xml())
		# FIXME: this is a little bit inefficient, since we prob. generate the string twice
		ET.SubElement(param, 'payload-length').text = str(len(str(self)))
		# currently string representation is hard coded
		ET.SubElement(param, 'acl-representation').text = 'fipa.acl.rep.string.std'
		now = datetime.utcnow()
		ts = "{0}{1:03d}".format(now.strftime("%Y%m%dZ%H%M%S"), int(now.microsecond / 1000))
		ET.SubElement(param, 'date').text = ts
		return ET.tostring(root, encoding='unicode', method='xml')

	def __str__(self):
		FIPA_PARAMETERS = ['sender', 'receiver', 'content', 'reply-with', 'language', 'ontology', 'protocol']
		s = '(' + self.performative.name + ' '
		parameters = vars(self)
		for pp in FIPA_PARAMETERS:
			key = pp.replace('-', '_')
			if key in parameters:
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

if __name__ == "__main__":
	acl_msg = ACLMessage(Performative.INFORM)
	acl_msg.sender     = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
	acl_msg.receivers += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name \"\\"192.168.122.1:1099/JADE\\"\" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
	acl_msg.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"

	print(acl_msg)

	print(acl_msg.generateEnvelope())

	print(ET.dump(acl_msg.sender.xml()))
