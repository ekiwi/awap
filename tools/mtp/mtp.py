#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mtp.py

import http.client
import urllib.parse
import queue, threading, re
from fipa.acl import ACLMessage, ACLEnvelope, Performative, AgentIdentifier

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
	def __init__(self, addresse):
		self.boundary = "a1723f6311bdcdc73e4145537302b33"

		self.tx_headers = {
			"Content-type": "multipart/mixed ; boundary=\"{}\"".format(self.boundary),
			"Connection": "keep-alive"}
		self.tx_queues = []

		self.rx_queue = queue.Queue()
		self.rx_server = MTPServer(addresse, self.rx_queue)
		self.rx_thread = threading.Thread(target=self.receiver)
		# self.rx_thread.setDaemon(True)
		self.rx_thread.start()

	def send(self, env):
		if isinstance(env, ACLMessage):
			env = ACLEnvelope.from_msg(msg)
		if isinstance(env, ACLEnvelope):
			env_txt = ET.tostring(env.xml(), encoding='unicode', method='xml')
			body = msg_frmt.format(env_txt, env.msg.mime_type, env.msg)
			body = ''.join((line + '\r\n') for line in body.splitlines())
			for receiver in env.receiver:
				# FIXME: currently only supports one address per receiver
				url = receiver.addresses[0]
				if not url in self.rx_queues:
					qq = queue.Queue()
					tx_thread = threading.Thread(target=self.sender, args=[url, qq])
					tx_thread.start()
					self.tx_queues[url] = qq
				self.tx_queues[url].put(body)

	def receive(self):
		return self.rx_queue.get()

	def sender(self, url, tx_queue):
		""" Thread that is responsible for sending ACLMessages
		"""
		tx = http.client.HTTPConnection(self.url)
		while True:
			env = tx_queue.get()
			if env is None:
				break
			tx.request("POST", "", body, self.tx_headers)
			response = tx.getresponse()
			if response.reason != "OK":
				print("Error: failed to send message")
			tx_queue.task_done()
		tx.close()

	def receiver(self):
		""" Thread that is responsible for receiving ACLMessages
		"""
		self.rx_server.serve_forever()


class MTPHandler(BaseHTTPRequestHandler):
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
			self.send_error(406)	# TODO: what is the correct code?
			return
		env = ACLEnvelope.from_mtp(envelope, message)
		if env.acl_representation != 'fipa.acl.rep.string.std':
			print("Error: envelope specifies `{}`. Can only read fipa.acl.rep.string.std.".format(env.representation))
			self.send_error(406)	# TODO: what is the correct code?
			return
		self.server.rx_queue.put(env)
		self.send_ok()

	def send_ok(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(b"<html><body><h1>200 OK</h1></body></html>")

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


class MTPServer(HTTPServer):
	def __init__(self, addresse, rx_queue):
		self.rx_queue = rx_queue
		super().__init__(addresse, MTPHandler)

if __name__ == "__main__":
#	mtp = Mtp("130-000.eduroam.rwth-aachen.de:7778")
#	mtp.send(acl_msg)

#	# TODO: implement in Mtp method
#	mtp.tx_queue.join()
#	print("done")
#	mtp.tx_queue.put(None)


	mtp = Mtp(('', 9000))

	while True:
		env = mtp.receive()
		print(env.msg)






