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

<?xml version="1.0"?>
<envelope><params index="1"><to><agent-identifier><name>rma@192.168.122.1:5000/JADE</name><addresses><url>http://ip2-127.halifax.rwth-aachen.de:57727/acc</url></addresses></agent-identifier></to><from><agent-identifier><name>ams@192.168.122.1:1099/JADE</name><addresses><url>http://ip2-127.halifax.rwth-aachen.de:7778/acc</url></addresses></agent-identifier></from><acl-representation>fipa.acl.rep.string.std</acl-representation><payload-length>873</payload-length><date>20150630Z130133800</date><intended-receiver><agent-identifier><name>rma@192.168.122.1:5000/JADE</name><addresses><url>http://ip2-127.halifax.rwth-aachen.de:57727/acc</url></addresses></agent-identifier></intended-receiver></params></envelope>
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
	acl_msg.sender    = AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc")
	acl_msg.receiver += [AgentIdentifier("ams@192.168.122.1:5000/JADE", "http://ip2-127.halifax.rwth-aachen.de:57727/acc")]
	acl_msg.content = '"((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name \"\\"192.168.122.1:1099/JADE\\"\" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))"'
	acl_msg.reply_with = "rma@192.168.122.1:5000/JADE1435662093800"
	acl_msg.language = "fipa-sl0"
	acl_msg.ontology = "FIPA-Agent-Management"
	acl_msg.protocol = "fipa-request"


#	body = msg	#"--{0}\r\n(inform)\r\n--{0}--\r\n".format(boundary)

	body = msg.format(acl_msg.mime_type, acl_msg)

	body = ''.join((line + '\r\n') for line in body.splitlines())

	headers = {"Content-type": "multipart/mixed ; boundary=\"{}\"".format(boundary), "Connection": "keep-alive"}

	conn = http.client.HTTPConnection("ip2-127.halifax.rwth-aachen.de:7778")
	conn.request("POST", "", body, headers)

	response = conn.getresponse()
	print(response.status, response.reason)
	print(response.read())

	conn.close()
