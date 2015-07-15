#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ams.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from fipa import FP0Parser


class AMS(ACLCommunicator):
	def __init__(self, platform_name, mtp):
		self.platform_name = platform_name
		super().__init__('ams@{}'.format(self.platform_name), mtp)
		self.parser = FP0Parser()

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
		print("AMS: received answer")
		print(answer.content)
		res = self.parser.parse_content(answer.content)
		ap_description = res[0][3][0][1]
		if ap_description['name'] != 'ap-description':
			print('ERROR: was not able to find ap-description in `{}`'.format(res))
			return
		print("AP Name: ".format(ap_description['terms']['name']))
		for service in ap_description['terms']['ap-services']:
			s_name = service[1]['terms']['name']
			s_type = service[1]['terms']['type']
			s_addresses = service[1]['terms']['addresses']
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
		print(res[0][2])
