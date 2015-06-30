#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# acl.py

"""
	This library provides an incomplete subset of the FIPA ACL
	Message Representation in String Specification (SC00070I)
	http://www.fipa.org/specs/fipa00070/SC00070I.html
"""

from enum import Enum

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

class ACLMessage(object):
	def __init__(self, performative):
		self.mime_type = "application/text"
		self.performative = performative
		self.sender = None
		self.receiver = []
		self.content = None
		self.reply_with = None
		self.language = None
		self.ontology = None
		self.protocol = None

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
	acl_msg.sender    = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
	acl_msg.receiver += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name \"\\"192.168.122.1:1099/JADE\\"\" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
	acl_msg.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"

	print(acl_msg)
