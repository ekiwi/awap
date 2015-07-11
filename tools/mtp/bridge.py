#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# bridge.py

from mtp import MTP, ACLCommunicator, AgentIdentifier, Performative
from ams import AMS

if __name__ == "__main__":
	mtp = MTP("http://localhost:9000/acc")
	ams = AMS("awap", mtp)
	ams.discover_ams(AgentIdentifier("ams@192.168.122.1:1099/JADE", "http://ip2-127.halifax.rwth-aachen.de:7778/acc"))

