#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# bridge.py

import os, sys, json, threading, queue
from awap import Awap
from udp import Dispatcher
tools_path = os.path.join('..')
sys.path.append(tools_path)
from mtp import *

class BroadcastBridge(ACLCommunicator):
	def __init__(self, parent):
		assert(isinstance(parent, Bridge))
		assert(isinstance(parent.mtp, MTP))
		assert(isinstance(parent.df_id, AgentIdentifier))
		super().__init__('broadcasts@{}'.format(parent.platform_name), parent.mtp)
		self.parent = parent
		self.dispatcher = parent.dispatcher
		self.df = DF(self, parent.df_id)
		self.desc = DFAgentDescription(
			ServiceDescription("BridgeService", "Blablabla"),
			self.id)
		self._rx_thread = threading.Thread(target=self._receiver)
		self.running = False

	def register(self):
		success = self.df.register(self.desc)
		if success:
			self.running = True
			self._rx_thread.start()
		return success

	def deregister(self):
		self.running = False
		return self.df.deregister(self.desc)

	def _receiver(self):
		while self.running:
			msg = self.receive()
			print("BroadcastBridge received:")
			print(msg.content)

			# create message
			content = json.loads(msg.content)
			message = json.loads(content['Message'])
			service_desc = json.loads(content['ServiceDescription'])

			dd = { 'IsBroadcast': True,
				   'SourceAgent': self.parent.fipa_name_to_id(msg.sender),
				   'DestinationAgent': 0, # dummy value
				   'Content': message }
			bb = Awap.message_to_bin(dd) + Awap.service_desc_to_bin(service_desc)
			self.dispatcher.sendto(bb)

class AgentBridge(ACLCommunicator):
	@staticmethod
	def generate_name(ip_addr, agent_id):
		return "{}AgentId{}".format(ip_addr, agent_id)

	def __init__(self, ip_addr, agent_id, parent):
		assert(isinstance(parent, Bridge))
		assert(isinstance(parent.mtp, MTP))
		assert(isinstance(parent.df_id, AgentIdentifier))
		name = AgentBridge.generate_name(ip_addr, agent_id)
		super().__init__('{}@{}'.format(name, parent.platform_name), parent.mtp)
		self.name = name
		self.parent = parent
		self.dispatcher = parent.dispatcher
		self.ip = ip_add
		self.agent_id = agent_id
		self.df = DF(self, parent.df_id)
		self._rx_thread = threading.Thread(target=self._receiver)
		self._rx_thread.start()

	def send(self, rec_fipa_id, data):
		assert(isinstance(data, bytes))
		dd = Awap.message_to_dict(data)
		msg = self.create_msg(dd['performative'], rec_fipa_id)
		msg.content = json.dumps(dd['content'])
		self.send(msg)

	def sendBroadcast(self, data):
		assert(isinstance(data, bytes))
		dd = Awap.message_to_dict(data)
		assert(dd['IsBroadcast'])
		service_desc = Awap.service_desc_to_dict(data[dd['Length']:])
		# find agents that offer service
		service = ServiceDescription(service_desc['service'])
		for name, value in service:
			if name != 'service':
				service.add_property(name, value)
		receivers = self.df.search(service)
		# create broadcast message
		msg = self.create_msg(dd['performative'], receivers)
		msg.content = json.dumps(dd['content'])
		self.send(msg)

	def _receiver(self):
		while True:
			msg = self.receive()
			print("AgentBridge ({}) received:".format(self.name))
			print(msg.content)
			# create message
			dd = { 'IsBroadcast': False,
				   'SourceAgent': self.parent.fipa_name_to_id(msg.sender),
				   'DestinationAgent': self.agent_id,
				   'Content': json.loads(msg.content) }
			bb = Awap.message_to_bin(dd)
			# send through dispatcher
			self.dispatcher.sendto(self.ip, Awap.message_to_bin(dd))

class Bridge():
	def __init__(self, local_url, dispatcher, platform_name="awap-bridge"):
		self.mtp = MTP(local_url)
		self.platform_name = platform_name
		self.dispatcher = dispatcher
		self.broadcast_bridge = None
		self.agent_bridges = {}
		self.df_id = None
		self._jade_agents_by_name = {}
		self._jade_agents_by_id = {}
		self._agent_ids = list(range(0,8))

	def register(self, jade_url):
		""" Registers the Bridge Broadcast service with a running JADE instance
		"""
		# find df
		with AMS("awap", self.mtp) as ams:
			agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))
			self.df_id = next(agent['name'] for agent in agents if agent['name'].name.startswith('df@'))
			print("found df: {}".format(self.df_id))
		self.broadcast_bridge = BroadcastBridge(self)
		return self.broadcast_bridge.register()

	def deregister(self):
		self.broadcast_bridge.deregister()

	def fipa_name_to_id(self, fipa_id):
		assert(isinstance(fipa_id, AgentIdentifier))
		try:
			return self._jade_agents_by_name[fipa_id]
		except KeyError:
			assert(len(self._agent_ids) > 0)
			agent_id = self._agent_ids.pop()
			self._jade_agents_by_name[fipa_id] = agent_id
			self._jade_agents_by_id[agent_id] = fipa_id
			return agent_id

	def id_to_fipa_name(self, agent_id):
		assert(isinstance(agent_id, int))
		# if this entry does not exist, something somewhere went terribly wrong
		return self._jade_agents_by_id[agent_id]

	def _receiver(self):
		while True:
			(addr, data) = self.dispatcher.receive()
			# decode message
			dd = Awap.message_to_dict(data)

			# find sender agent bridge
			name = AgentBridge.generate_name(addr, dd['SourceAgent'])
			if not name in self.agent_bridges:
				self.agent_bridges[name] = AgentBridge(addr, dd['SourceAgent'], self)
			bridge = self.agent_bridges[name]

			# dispatch messge
			if dd['IsBroadcast']:
				bridge.sendBroadcast(data)
			else:
				bridge.send(self.id_to_fipa_name(dd['DestinationAgent']), data)



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Use: {} JADE_URL".format(sys.argv[0]))
		sys.exit(1)

	# load communication specification
	path = os.path.abspath(os.path.join('..', '..', 'example', 'communication'))
	conf = os.path.abspath(os.path.join('..', '..', 'example', 'configuration.xml'))
	Awap.load_xml(path, conf)

	# create network interfaces and start them
	jade_url = sys.argv[1]
	dispatcher = Dispatcher(("255.255.255.255", 5005), src_port=6006)
	bridge = Bridge("http://localhost:9000/acc", dispatcher)
	bridge.register(jade_url)

	#(serv, msg) = bridge.broadcasts.receiveBroadcast()
	#print("serv ", serv)
	#print("msg ", msg)

	import time
	time.sleep(10)

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
