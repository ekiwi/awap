#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# bridge.py

import sys
from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from ams import AMS
from df import DF, ServiceDescription

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Use: {} JADE_URL".format(sys.argv[0]))
		sys.exit(1)
	jade_url = sys.argv[1]
	mtp = MTP("http://localhost:9000/acc")
	ams = AMS("awap", mtp)
	agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))

	df_id = next(agent['name'] for agent in agents if agent['name'].name.startswith('df@'))
	print("found df: {}".format(df_id))
	df = DF("awap", mtp)
	service = ServiceDescription("TemperatureService")
	service.add_property("building", "Build1")
	service.add_property("room", "R1")
	df.search(df_id, service)
