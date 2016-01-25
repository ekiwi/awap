#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# df.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from fipa import FP0Parser, AlternativeFP0ObjectFactory

import unittest


class FP0(object):
	FP0ParserSingleton = None

	@staticmethod
	def getParser():
		if FP0.FP0ParserSingleton is None:
			FP0.FP0ParserSingleton = FP0Parser(AlternativeFP0ObjectFactory())
		return FP0.FP0ParserSingleton

	@staticmethod
	def createConstantString(value):
		""" Tries to turn the value into a valid Constant
		"""
		if isinstance(value, list):
			s  = '(set '
			s += ' '.join([FP0.createConstantString(v) for v in value])
			s += ' )'
			return s
		elif isinstance(value, str):
			# test if this is a Word or a StringLiteral
			return value if FP0.getParser().is_Word(value) else FP0.makeStringLiteral(value)
		elif isinstance(value, int):
			return str(value)
		elif isinstance(value, float):
			raise Exception("ERROR: float constants aren't supported yet")
		else:
			return str(value)

	@staticmethod
	def makeStringLiteral(value):
		return '"{}"'.format(value.replace('"', '\\"'))

class ServiceDescription(object):
	def __init__(self, service_type, name=None):
		self.name = name
		self.type = service_type
		self.properties = []

	def add_property(self, name, value):
		self.properties.append((name, value))

	def __str__(self):
		s  = "(service-description"
		if self.name is not None and len(self.name) > 0:
			s += " :name " + FP0.createConstantString(self.name)
		s += " :type " + FP0.createConstantString(self.type) + " :properties (set"
		for pp in self.properties:
			s += " (property :name "
			s += FP0.createConstantString(pp[0]) + " :value "
			s += FP0.createConstantString(pp[1]) + ")"
		s += "))"
		return s


class DFAgentDescription(object):
	def __init__(self, service_desc, agent_id = None):
		assert (agent_id is None or isinstance(agent_id, AgentIdentifier))
		assert isinstance(service_desc, ServiceDescription)
		self.name = agent_id
		self.service = service_desc

	def __str__(self):
		s = "(df-agent-description"
		if self.name is not None and isinstance(self.name, AgentIdentifier) > 0:
			s += " :name " + FP0.createConstantString(self.name)
		if self.service is not None:
			s += " :services (set {})".format(self.service)
		return s + ")"

class DF(ACLCommunicator):
	def __init__(self, platform_name, mtp):
		self.platform_name = platform_name
		super().__init__('df@{}'.format(self.platform_name), mtp)
		self.parser = FP0.getParser()

	def create_msg(self, performative, receiver=None):
		msg = super().create_msg(performative, receiver)
		msg.language = "fipa-sl0"
		msg.ontology = "FIPA-Agent-Management"
		msg.protocol = "fipa-request"
		return msg

	def create_action_msg(self, action, receiver=None):
		msg = self.create_msg(Performative.REQUEST, receiver)
		msg.content = '((action {} {}))'.format(receiver, action)
		return msg

	def search(self, df_id, service_desc):
		assert isinstance(service_desc, ServiceDescription)
		action = '(search {}'.format(DFAgentDescription(service_desc))
		action += ' (search-constraints :min-depth 2))'
		self.send(self.create_action_msg(action, df_id))

		answer = self.receive()
		if answer.performative != Performative.INFORM:
			print("ERROR: Unexpected answer:\n{}".format(answer))
			return
		res = self.parser.parse_content(answer.content)

		agents = []
		for desc in res[0][2]:
			if desc[0] == 'df-agent-description':
				agents.append(desc[1]['name'])
		return agents

	def register(self, df_id, agent_desc):
		assert isinstance(agent_desc, DFAgentDescription)
		action = '(register {})'.format(agent_desc)
		self.send(self.create_action_msg(action, df_id))

		answer = self.receive()
		return answer.performative == Performative.INFORM


class TestServiceDescription(unittest.TestCase):
	def setUp(self):
		self.service = ServiceDescription("the best kind", "test_service")
		self.service.add_property("age", "old")


	def test_to_string(self):
		print(self.service)

if __name__ == "__main__":
	unittest.main()
