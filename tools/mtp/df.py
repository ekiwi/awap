#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# df.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from fipa import FP0Parser

import unittest


class FP0(object):
	FP0ParserSingleton = None

	@staticmethod
	def getParser():
		if FP0.FP0ParserSingleton is None:
			FP0.FP0ParserSingleton = FP0Parser()
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
	def __init__(self, name, service_type):
		assert isinstance(name, str)
		self.name = name
		self.type = service_type
		self.properties = []

	def add_property(self, name, value):
		self.properties.append((name, value))

	def __str__(self):
		s  = "(service‑description :name " + FP0.createConstantString(self.name)
		s += " :type " + FP0.createConstantString(self.type) + " :properties (set"
		for pp in self.properties:
			s += " (property :name "
			s += FP0.createConstantString(pp[0]) + " :value "
			s += FP0.createConstantString(pp[1]) + ")"
		s += "))"
		return s


class DFAgentDescription(object):
	def __init__(self, agent_id, service_desc):
		assert isinstance(agent_id, AgentIdentifier)
		assert isinstance(service_desc, ServiceDescription)
		self.name = agent_is
		self.service = service_desc

class DF(ACLCommunicator):
	def __init__(self, platform_name, mtp):
		self.platform_name = platform_name
		super().__init__('df@{}'.format(self.platform_name), mtp)
		self.parser = FP0.getParser()



class TestServiceDescription(unittest.TestCase):
	def setUp(self):
		self.service = ServiceDescription("test_service", "the best kind")
		self.service.add_property("age", "old")


	def test_to_string(self):
		print(self.service)

if __name__ == "__main__":
	unittest.main()
