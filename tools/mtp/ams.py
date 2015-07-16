#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ams.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from fipa import FP0Parser, FP0ObjectFactory


class CustomFP0ObjectFactory(FP0ObjectFactory):
	def create_FunctionalTerm(self, name, terms):
		if name == 'agent-identifier':
			(id_name, id_addresses) = (None, [])
			for term in terms:
				if term[0] == 'name': id_name = term[1]
				elif term[0] == 'addresses': id_addresses = term[1]
			if id_name:
				return AgentIdentifier(id_name, id_addresses)
		terms = self._terms_to_list_or_dict(terms)
		return (name, terms)

	def create_AtomicFormula(self, tokens):
		if len(tokens) == 1 and tokens[0] == 'true':
			return True
		elif len(tokens) == 1 and tokens[0] == 'false':
			return False
		elif len(tokens) == 1:
			return str(tokens[0])
		elif tokens[0] == 'result':
			return ('result', tokens[1], tokens[2])
		else:
			terms = tokens[1:]
			return (str(tokens[0]), terms)


class AMS(ACLCommunicator):
	def __init__(self, platform_name, mtp):
		self.platform_name = platform_name
		super().__init__('ams@{}'.format(self.platform_name), mtp)
		self.parser = FP0Parser(CustomFP0ObjectFactory())

	def create_msg(self, performative, receiver=None):
		msg = super().create_msg(performative, receiver)
		msg.language = "fipa-sl0"
		msg.ontology = "FIPA-Agent-Management"
		msg.protocol = "fipa-request"
		return msg

	def discover_ams(self, foreign_ams_id):
		msg = self.create_msg(Performative.REQUEST, foreign_ams_id)
		msg.content = '((action {} (get-description)))'.format(foreign_ams_id)
		self.send(msg)
		answer = self.receive()
		if answer.performative != Performative.INFORM:
			print("ERROR: Unexpected answer:\n{}".format(answer))
			return
		res = self.parser.parse_content(answer.content)
		ap_description = res[0][2][0]
		if ap_description[0] != 'ap-description':
			print('ERROR: was not able to find ap-description in `{}`'.format(res))
			return
		print("AP Name: ".format(ap_description[1]['name']))
		for service in ap_description[1]['ap-services']:
			s_name = service[1]['name']
			s_type = service[1]['type']
			s_addresses = service[1]['addresses']
			print("Found service: {}({}) @ {}".format(s_name, s_type, s_addresses))

	def discover_agents(self, foreign_ams_id):
		msg = self.create_msg(Performative.REQUEST, foreign_ams_id)
		action = '(search (ams-agent-description) (search-constraints :max-results -1))'
		msg.content = '((action {} {}))'.format(foreign_ams_id, action)
		self.send(msg)
		answer = self.receive()
		if answer.performative != Performative.INFORM:
			print("ERROR: Unexpected answer:\n{}".format(answer))
			return
		print("AMS: received answer")
		print(answer.content)
		res = self.parser.parse_content(answer.content)
		print(res)
		print("--------------------------------------")
		for desc in res[0][2]:
			if desc[0] == 'ams-agent-description':
				print('Found Agent: {}'.format(desc[1]))
				state = desc[1]['state']






