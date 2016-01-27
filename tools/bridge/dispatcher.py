#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# dispatcher.py


import queue, threading, socket, json
import os, sys
from awap import Awap
tools_path = os.path.join('..')
sys.path.append(tools_path)
from mtp import ACLMessage, Performative, AgentIdentifier

class Dispatcher():
	def __init__(self, multicast_addr, src_port=6006):
		self.multicast_addr = multicast_addr
		self._jade_agents_by_name = {}
		self._jade_agents_by_id = {}
		self._agent_ids = list(range(0,8))

		self._rx_queue = None
		self._rx_thread = threading.Thread(target=self._receiver)
		self._rx_thread.start()
		self._tx_port = multicast_addr[1]
		self._tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._tx_sock.bind(('0.0.0.0', src_port))

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

	def send_broadcast(self, msg):
		assert(isinstance(msg, ACLMessage))

		# create message
		content = json.loads(msg.content)
		message = json.loads(content['Message'])
		service_desc = json.loads(content['ServiceDescription'])

		dd = { 'IsBroadcast': True,
		       'SourceAgent': self.fipa_name_to_id(msg.sender),
		       'DestinationAgent': 0, # dummy value
		       'Content': content }
		bb = Awap.message_to_bin(dd) + Awap.service_desc_to_bin(service_desc)
		self._sendto(bb, self.multicast_addr)

	def send(self, dest_ip, dest_agent_id, msg):
		assert(isinstance(msg, ACLMessage))

		# create message
		dd = { 'IsBroadcast': False,
		       'SourceAgent': self.fipa_name_to_id(msg.sender),
		       'DestinationAgent': dest_agent_id,
		       'Content': json.loads(msg.content) }
		bb = Awap.message_to_bin(dd)
		self._sendto(bb, dest_ip)

	def _sendto(self, bb, ip_addr):
		self._tx_sock.sendto(bb, (ip_addr, self._tx_port))
		print('--------------------------------------')
		print('[UDP] Sending to {} on port {}'.format(ip_addr, self._tx_port))
		print(bb)
		print('--------------------------------------')

	def register_receiver(self, queue):
		if self._rx_queue is not None:
			print("Dispatcher: WARN: overwriting receiver queue")
		self._rx_queue = queue

	def deregister_receiver(self):
		self._rx_queue = None

	def _receiver(self):
		""" Thread that is responsible for receiving ACLMessages
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(self.multicast_addr)

		while True:
			data, addr = sock.recvfrom(1024)
			if self._rx_queue is None:
				print("WARNING: received message, but no receiver queue available")
				print("from sender: {}".format(addr))
				print(data)
			else:
				self._rx_queue.put((addr, data))



if __name__ == "__main__":
	path = os.path.abspath(os.path.join('..', '..', 'example', 'communication'))
	conf = os.path.abspath(os.path.join('..', '..', 'example', 'configuration.xml'))
	Awap.load_xml(path, conf)

	d = Dispatcher(("127.0.0.1", 5005))
	qq = queue.Queue()
	d.register_receiver(qq)

	# inform temperatur message
	msg = ACLMessage(Performative.INFORM)
	msg.sender = AgentIdentifier("TestTemperatureSensor", "https://test.de")
	msg.content = json.dumps({'message': 'Temperature', 'service': 'TemperatureService', 'value': 1993})

	d.send("127.0.0.1", 7, msg)

	(addr, data) = qq.get()
	print("------------------------")
	print("from: ", addr)
	print("raw:  ", data)
	print("dict: ", Awap.message_to_dict(data))

