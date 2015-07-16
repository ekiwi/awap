#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# bridge.py

import sys
from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from ams import AMS

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Use: {} JADE_URL".format(sys.argv[0]))
		sys.exit(1)
	jade_url = sys.argv[1]
	mtp = MTP("http://localhost:9000/acc")
	ams = AMS("awap", mtp)
	agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))
	print("Agents @ {}".format(jade_url))
	for agent in agents:
		name = agent['name']
		print("{} @ {} ({})".format(name.name, name.addresses, agent['state']))

