#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mtp.py

import http.client
import urllib.parse
from fipa.acl import ACLMessage, Performative, AgentIdentifier

msg = """
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
	def __init__(self):
		pass

#	def 


if __name__ == "__main__":
	boundary = "a1723f6311bdcdc73e4145537302b33"

	acl_msg = ACLMessage(Performative.INFORM)
	acl_msg.sender     = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
	acl_msg.receivers += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name 192.168.122.1:1099/JADE :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
	acl_msg.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"


	body = msg.format(acl_msg.generateEnvelope(), acl_msg.mime_type, acl_msg)
	body = ''.join((line + '\r\n') for line in body.splitlines())
	print(body)

	headers = {"Content-type": "multipart/mixed ; boundary=\"{}\"".format(boundary), "Connection": "keep-alive"}

	conn = http.client.HTTPConnection("ip2-127.halifax.rwth-aachen.de:7778")
	conn.request("POST", "", body, headers)

	response = conn.getresponse()
	print(response.status, response.reason)
	print(response.read())

	conn.close()
