/**
 * node.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "node.hpp"
#include <util.hpp>

namespace awap {

Node::Node(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress)
	: vm(vm), awapCommon(awapCommon), awapMote(awapMote), address(nodeAddress)
{
}

Node::~Node()
{
	for(auto agent : this->agents) {
		if(agent != nullptr) {
			delete agent;
		}
	}
}

void
Node::loadAgent(const uint8_t* content, const size_t length)
{
	for(size_t ii = 0; ii < arrayCount(agents); ++ii) {
		if(agents[ii] == nullptr) {
			Agent* agent = Agent::fromPacket(*this, ii, content, length);
			if(agent != nullptr) {
				agents[ii] = agent;
				// TODO: should setup be called from somewhere else?
				agent->setup();
			}
			break;
		}
	}
}

void
Node::receive(const NodeAddress sender, const uint8_t* content, const size_t length)
{
	// TODO!
}

} // namespace awap
