#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# dispatcher.py


import queue, threading, re, sys, socket


class AwapMessage():
	def __init__(self):
		pass

	@property
	def bin_content(self):
		return b"unicast test"

	@property
	def receiver(self):
		return ("127.0.0.1", 5005)


class AwapBroadcast():
	def __init__(self):
		pass

	@property
	def bin_content(self):
		return b"broadcast test"

	@property
	def receiver(self):
		return ("255.255.255.255", 5005)


class Dispatcher():
	def __init__(self, multicast_addr, src_port=6006):
		self.multicast_addr = multicast_addr

		self._rx_queues = {}
		self._rx_thread = threading.Thread(target=self._receiver)
		self._rx_thread.start()
		self.tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.tx_sock.bind(('0.0.0.0', src_port))

	def send(self, msg):
		self.tx_sock.sendto(msg.bin_content, msg.receiver)
		print('--------------------------------------')
		print('[UDP] Sending to {}'.format(msg.receiver))
		print(msg.bin_content)
		print('--------------------------------------')

	def register_receiver(self, addr, queue):
		if addr in self._rx_queues and self._rx_queues[addr] != queue:
			print("WARN: overwriting queue registered for `{}`".format(addr))
		self._rx_queues[addr] = queue

	def deregister_receiver(self, addr):
		try:             del self._rx_queues[addr]
		except KeyError: pass

	def _receiver(self):
		""" Thread that is responsible for receiving ACLMessages
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(self.multicast_addr)

		while True:
			data, addr = sock.recvfrom(1024)
			# TODO: parse results
			if addr in self._rx_queues:
				self._rx_queues[addr].put(data)
			else:
				print("WARNING: received message from unregisterd sender: {}".format(addr))



if __name__ == "__main__":
	d = Dispatcher(("127.0.0.1", 5005))
	qq = queue.Queue()
	d.register_receiver(("127.0.0.1", 6006), qq)
	d.send(AwapMessage())

	data = qq.get()
	print("------------------------")
	print(data)

