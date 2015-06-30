#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mtp.py

import http.client
import urllib.parse
import queue, threading
from fipa.acl import ACLMessage, Performative, AgentIdentifier

msg_frmt = """
This is not part of the MIME multipart encoded message.
--a1723f6311bdcdc73e4145537302b33
Content-Type: application/xml

{}
--a1723f6311bdcdc73e4145537302b33
Content-Type: {}

{}
--a1723f6311bdcdc73e4145537302b33--

"""

class Mtp(object):
	def __init__(self, url):
		self.url = url
		self.boundary = "a1723f6311bdcdc73e4145537302b33"

		self.tx_headers = {
			"Content-type": "multipart/mixed ; boundary=\"{}\"".format(self.boundary),
			"Connection": "keep-alive"}
		self.tx = http.client.HTTPConnection(self.url)
		self.tx_msgs = queue.Queue()
		self.tx_thread = threading.Thread(target=self.sender)
		# self.tx_thread.setDaemon(True)
		self.tx_thread.start()

	def send(self, msg):
		if isinstance(msg, ACLMessage):
			self.tx_msgs.put(msg)

	def sender(self):
		""" Thread that is responsible for sending ACLMessages
		"""
		while True:
			msg = self.tx_msgs.get()
			if msg is None:
				break
			body = msg_frmt.format(msg.generateEnvelope(), msg.mime_type, msg)
			body = ''.join((line + '\r\n') for line in body.splitlines())
			self.tx.request("POST", "", body, self.tx_headers)
			response = self.tx.getresponse()
			if response.reason != "OK":
				print("Error: failed to send message")
			self.tx_msgs.task_done()
		self.tx.close()


if __name__ == "__main__":
#	boundary = "a1723f6311bdcdc73e4145537302b33"

	acl_msg = ACLMessage(Performative.INFORM)
	acl_msg.sender     = AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")
	acl_msg.receivers += [AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")]
	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:5000/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:5000/acc)) (get-description)) (sequence (ap-description :name 192.168.122.1:5000/JADE :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:5000/acc)))))))"'
	acl_msg.reply_with = "rma@192.168.122.1:1099/JADE1435662093800"
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"

	mtp = Mtp("ip2-127.halifax.rwth-aachen.de:7778")
	mtp.send(acl_msg)

	# TODO: implement in Mtp method
	mtp.tx_msgs.join()
	print("done")
	mtp.tx_msgs.put(None)
