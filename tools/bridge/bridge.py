#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# bridge.py

import os, sys, json
tools_path = os.path.join('..')
sys.path.append(tools_path)
from mtp import *

class BroadcastBridge(ACLCommunicator):
	def __init__(self, platform_name, mtp, df_id):
		assert(isinstance(mtp, MTP))
		assert(isinstance(df_id, AgentIdentifier))
		super().__init__('broadcasts@{}'.format(platform_name), mtp)
		self.df = DF(self, df_id)
		self.desc = DFAgentDescription(
			ServiceDescription("BridgeService", "Blablabla"),
			self.id)

	def register(self):
		return self.df.register(self.desc)

	def deregister(self):
		return self.df.deregister(self.desc)

	def sendBroadcast(self, service_desc, performative, content):
		assert(isinstance(service_desc, ServiceDescription))
		assert(isinstance(performative, Performative))
		if not isinstance(content, str):
			content = json.dumps(content)
		# find agents that offer service
		receivers = self.df.search(service_desc)
		# create broadcast message
		msg = self.create_msg(performative, receivers)
		msg.content = content
		self.send(msg)

	def receiveBroadcast(self):
		msg = self.receive()
		content = json.loads(msg.content)
		message = json.loads(content['Message'])
		service_description = json.loads(content['ServiceDescription'])
		return (service_description, message)


class Bridge():
	def __init__(self, local_url):
		self.mtp = MTP(local_url)
		self.broadcasts = None

	def register(self, jade_url):
		""" Registers the Bridge Broadcast service with a running JADE instance
		"""
		# find df
		with AMS("awap", self.mtp) as ams:
			agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))
			self.df_id = next(agent['name'] for agent in agents if agent['name'].name.startswith('df@'))
			print("found df: {}".format(self.df_id))
		self.broadcasts = BroadcastBridge("awap", self.mtp, self.df_id)
		return self.broadcasts.register()

	def deregister(self):
		self.broadcasts.deregister()



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Use: {} JADE_URL".format(sys.argv[0]))
		sys.exit(1)
	jade_url = sys.argv[1]
	bridge = Bridge("http://localhost:9000/acc")
	bridge.register(jade_url)

	(serv, msg) = bridge.broadcasts.receiveBroadcast()
	print("serv ", serv)
	print("msg ", msg)

	import time
	time.sleep(2)

	bridge.deregister()

"""
	# find DF
	agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))
	df_id = next(agent['name'] for agent in agents if agent['name'].name.startswith('df@'))
	print("found df: {}".format(df_id))
	# find agents that can supply temperature in Building1, Room1
	df = DF("awap", mtp)
	service = ServiceDescription("TemperatureService")
	service.add_property("building", "Build1")
	service.add_property("room", "R1")
	temperature_agents = df.search(df_id, service)
	print("found agents that provide a {}:".format(service.type))
	print("\n".join(str(a) for a in temperature_agents))

	# Broadcast: Bridge -> JADE
	# reguest temperature from agent(s)
	test = ACLCommunicator("test", mtp)
	msg = test.create_msg(Performative.REQUEST, temperature_agents)
	msg.content = json.dumps({'service': 'TemperatureService', 'message': 'RequestTemperature'})
	test.send(msg)
	# Unicast: JADE -> Bridge
	answer = test.receive()
	if answer.performative != Performative.INFORM:
		print("ERROR: Unexpected answer:\n{}".format(answer))
	else:
		print("Received Temperature: {}".format(json.loads(answer.content)['value']))

	# try to insert ourselves into df
	bridge_service = ServiceDescription("BridgeService", "Blablabla")
	df.register(df_id, DFAgentDescription(bridge_service, test.id))

	# receive broadcasts
	while True:
		# Broadcast: JADE -> Bridge
		msg = test.receive()
		content = json.loads(msg.content)
		message = json.loads(content['Message'])
		service_description = json.loads(content['ServiceDescription'])
		print('Message: ', message)
		print('Service Description: ', message)

		# Unicast: Bridge -> JADE
		answer = test.create_msg(Performative.INFORM, msg.sender)
		answer.content = json.dumps({'service': 'TemperatureService', 'message': 'Temperature', 'value': 36})
		test.send(answer)

	# TODO: clean up on close, i.e. remove entries from foreign DF
"""