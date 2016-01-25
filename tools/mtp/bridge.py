#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2016 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

# bridge.py

import sys, json
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
	# find DF
	agents = ams.discover_agents(AgentIdentifier("ams@192.168.122.1:1099/JADE", jade_url))
	df_id = next(agent['name'] for agent in agents if agent['name'].name.startswith('df@'))
	print("found df: {}".format(df_id))
 	# find agents that can supply temperature in Building1, Room1
	df = DF("awap", mtp)
	service = ServiceDescription("TemperatureService")
	service.add_property("building", "Build1")
	service.add_property("room", "R1")
	temperature_agents = df.search(df_id, service)
	print("found agents that provide a {}:".format(service.type))
	print("\n".join(str(a) for a in temperature_agents))

	# reguest temperature from agent(s)
	test = ACLCommunicator("test", mtp)
	msg = test.create_msg(Performative.REQUEST, temperature_agents)
	msg.content = json.dumps({'service': 'TemperatureService', 'message': 'RequestTemperature'})
	test.send(msg)
	answer = test.receive()
	if answer.performative != Performative.INFORM:
		print("ERROR: Unexpected answer:\n{}".format(answer))
	else:
		print("Received Temperature: {}".format(json.loads(answer.content)['value']))


