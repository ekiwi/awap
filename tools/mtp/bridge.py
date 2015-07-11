#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# bridge.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative

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

