#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mtp.py

import http.client
import urllib.parse
import queue, threading, re
from fipa.acl import ACLMessage, ACLEnvelope, Performative, AgentIdentifier

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

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

class MTP(object):
	def __init__(self, url):
		self.url = url
		self._boundary = "a1723f6311bdcdc73e4145537302b33"

		self._tx_headers = {
			"Content-type": "multipart/mixed ; boundary=\"{}\"".format(self._boundary),
			"Connection": "keep-alive"}
		self._tx_queues = {}

		pp = urlparse(self.url)
		self._rx_queues = {}
		self._rx_server = MTPServer((pp.hostname, pp.port), self._process_packet)
		self._rx_thread = threading.Thread(target=self._receiver)
		self._rx_thread.start()

	def send(self, env):
		if isinstance(env, ACLMessage):
			env = ACLEnvelope.from_message(env)
		if isinstance(env, ACLEnvelope):
			body = msg_frmt.format(env.xml_string(), env.msg.mime_type, env.msg)
			body = ''.join((line + '\r\n') for line in body.splitlines())
			for receiver in env.receiver:
				# FIXME: currently only supports one address per receiver
				url = receiver.addresses[0]
				if not url in self._tx_queues:
					qq = queue.Queue()
					tx_thread = threading.Thread(target=self._sender, args=[url, qq])
					tx_thread.start()
					self._tx_queues[url] = qq
				self._tx_queues[url].put(body)
		print('--------------------------------------')
		print('Sending')
		print('=======')
		print(env.msg)
		print('--------------------------------------')

	def register_receiver(self, name, queue):
		if name in self._rx_queues and self._rx_queues[name] != queue:
			print("WARN: overwriting queue registered for `{}`".format(name))
		self._rx_queues[name] = queue

	def _process_packet(self, envelope):
		""" Called by the HTTPServer in it's own thread.
			Distributes packets to the correct receiver queue
		"""
		print('--------------------------------------')
		print('Received')
		print('========')
		print(envelope.msg)

		for receiver in envelope.receiver:
			if receiver.name in self._rx_queues:
				self._rx_queues[receiver.name].put(envelope)
			else:
				print('\nERROR: could not deliver packet to `{}`'.format(receiver.name))

		print('--------------------------------------')

	def _sender(self, url, tx_queue):
		""" Thread that is responsible for sending ACLMessages
		"""
		tx = http.client.HTTPConnection(urlparse(url).netloc)
		while True:
			body = tx_queue.get()
			if body is None:
				break
			tx.request("POST", "", body, self._tx_headers)
			response = tx.getresponse()
			if response.reason != "OK":
				print("Error: failed to send message")
			tx_queue.task_done()
		tx.close()

	def _receiver(self):
		""" Thread that is responsible for receiving ACLMessages
		"""
		self._rx_server.serve_forever()


class MTPHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		length = int(self.headers.get('content-length'))
		ct = self.headers.get('content-type')
		boundary = re.search(r'boundary=-*"*(?P<b>[a-z0-9]+)', ct).group("b")
		body = self.rfile.read(length).decode('utf8')
		# initialize regex matchers
		self.re_bd = re.compile(r'--{}\s*'.format(boundary))
		self.re_ct = re.compile(r'content-type:\s+(?P<ct>[a-z]+/[a-z]+)', re.IGNORECASE)
		(envelope, env_mime, pos) = self._parse_multipart(body, 0)
		(message,  msg_mime, pos) = self._parse_multipart(body, pos)
		if env_mime != "application/xml" or msg_mime != "application/text":
			print("Error: did not receive the correct mime type")
			self.send_error(406)	# TODO: what is the correct code?
			return
		env = ACLEnvelope.from_mtp(envelope, message)
		if env.acl_representation != 'fipa.acl.rep.string.std':
			print("Error: envelope specifies `{}`. Can only read fipa.acl.rep.string.std.".format(env.representation))
			self.send_error(406)	# TODO: what is the correct code?
			return
		self.server._process_packet(env)
		self._send_ok()

	def _send_ok(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(b"<html><body><h1>200 OK</h1></body></html>")

	def _parse_multipart(self, body, pos):
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


class MTPServer(HTTPServer):
	def __init__(self, addresse, _process_packet):
		self._process_packet = _process_packet
		super().__init__(addresse, MTPHandler)


class ACLCommunicator(object):
	""" Base class for all services/agents that have a AgentIdentifier and
		need to use the MTP to communicate.
	"""
	def __init__(self, name, mtp):
		assert isinstance(mtp, MTP)
		self.id = AgentIdentifier(name, mtp.url)
		self._mtp = mtp
		self._rx_queue = queue.Queue()
		self._mtp.register_receiver(self.id.name, self._rx_queue)

	def send(self, msg):
		self._mtp.send(msg)

	def receive(self):
		msg = self._rx_queue.get()
		return msg

	def create_msg(self, performative, receiver=None):
		msg = ACLMessage(performative)
		msg.sender = self.id
		if receiver:
			if isinstance(receiver, list):
				msg.receiver += receiver
			else:
				msg.receiver.append(receiver)
		return msg

	def create_answer(self, performative, msg0):
		msg = ACLMessage(performative)
		msg.sender = self.id
		msg.receiver = [msg0.sender]
		msg.language = msg0.language
		msg.ontology = msg0.ontology
		msg.protocol = msg0.protocol
		msg.conversation_id = msg0.conversation_id
		msg.in_reply_to = msg0.reply_with
		return msg

if __name__ == "__main__":
	mtp = MTP("http://localhost:9000/acc")
	ams = ACLCommunicator("ams@awap", mtp)
	rec = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
	acl_msg = ams.create_msg(Performative.REQUEST, rec)
	acl_msg.content = '((action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)))'
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"
	ams.send(acl_msg)

