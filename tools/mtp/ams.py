#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ams.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative

class AMS(ACLCommunicator):
	def __init__(self, platform_name, mtp):
		self.platform_name = platform_name
		super().__init__('ams@{}'.format(self.platform_name), mtp)

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
