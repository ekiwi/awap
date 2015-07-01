#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mtp.py

import http.client
import urllib.parse
import queue, threading, re
from fipa.acl import ACLMessage, Performative, AgentIdentifier

from http.server import HTTPServer, BaseHTTPRequestHandler

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

	def receiver(self):
		""" Thread that is responsible for receiving ACLMessages
		"""
		pass


class CustomHTTPHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		length = int(self.headers.get('content-length'))
		ct = self.headers.get('content-type')
		boundary = re.search(r'boundary=-*"*(?P<b>[a-z0-9]+)', ct).group("b")
		body = self.rfile.read(length).decode('utf8')
		# initialize regex matchers
		self.re_bd = re.compile(r'--{}\s*'.format(boundary))
		self.re_ct = re.compile(r'content-type:\s+(?P<ct>[a-z]+/[a-z]+)', re.IGNORECASE)
		(envelope, env_mime, pos) = self.parse_multipart(body, 0)
		(message,  msg_mime, pos) = self.parse_multipart(body, pos)
		if env_mime != "application/xml" or msg_mime != "application/text":
			print("Error: did not receive the correct mime type")
		print("Envelope:")
		print(envelope)
		print("Message")
		print(message)

	def parse_multipart(self, body, pos):
		pos = self.re_bd.search(body, pos).end(0)
		m = self.re_ct.match(body, pos)
		if m is None:
			print('Error: failed to find content-type in multipart message."')
			return (None, None, pos)
		mime = m.group("ct")
		pos = m.end("ct")
		next_bound = self.re_bd.search(body, pos)
		content = body[pos:next_bound.start(0)]
		pos = next_bound.start()	# return start of boundary so that next call can find it again
		return (content, mime, pos)

	def do_GET(self):
		print("GET")
		print(self.headers)



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

#	mtp = Mtp("ip2-127.halifax.rwth-aachen.de:7778")
#	mtp.send(acl_msg)

#	# TODO: implement in Mtp method
#	mtp.tx_msgs.join()
#	print("done")
#	mtp.tx_msgs.put(None)


	httpd = HTTPServer(('', 9000), CustomHTTPHandler)
	httpd.serve_forever()






