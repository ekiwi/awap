#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# udp.py


import queue, threading, socket

class FakeNode():
	""" fakes a remote node on the network
	"""
	def __init__(self, dispatcher, name):
		assert(isinstance(dispatcher, Dispatcher))
		self.dispatcher = dispatcher
		self.name = name
		self.addr = "fake" + self.name

#	def send(self, bb):
#		self.dispatcher._rx_queue.put((self.addr))


class Dispatcher():
	def __init__(self, multicast_addr, src_port=6006):
		self.multicast_addr = multicast_addr[0]
		self.dest_port = multicast_addr[1]
		self.src_port = src_port

		self._rx_queue = queue.Queue()
		self._rx_thread = threading.Thread(target=self._receiver)
		self._rx_thread.start()
		self._tx_queue = queue.Queue()
		self._tx_thread = threading.Thread(target=self._sender)
		self._tx_thread.start()


	def sendto(self, ip_addr, bb = None):
		if bb is None and isinstance(ip_addr, bytes):
			bb = ip_addr
			ip_addr = self.multicast_addr
		self._tx_queue.put((ip_addr, bb))

	def receive(self):
		return self._rx_queue.get()

	def _receiver(self):
		""" Thread that is responsible for receiving UDP messages
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# bind to any address
		sock.bind(("", self.dest_port))

		while True:
			data, addr = sock.recvfrom(1024)
			if self._rx_queue is None:
				print("WARNING: received message, but no receiver queue available")
				print("from sender: {}".format(addr))
				print(data)
			else:
				port = addr[1]
				self._rx_queue.put((addr[0], data))

	def _sender(self):
		""" Thread that is responsible for sending UDP messages
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', self.src_port))
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		while True:
			(addr, data) = self._tx_queue.get()
			complete_addr = (addr, self.dest_port)
			# TODO: remove debug
			print('--------------------------------------')
			print('[UDP] Sending to {} on port {}'.format(complete_addr[0], complete_addr[1]))
			print(data)
			print('--------------------------------------')
			sock.sendto(data, complete_addr)

if __name__ == "__main__":
	d = Dispatcher(("255.255.255.255", 5005))
	d.sendto("127.0.0.1", b'hello unicast')
	d.sendto(b'hello broadcast')

	while True:
		(addr, data) = d.receive()
		print("------------------------")
		print("from: ", addr)
		print("raw:  ", data)

