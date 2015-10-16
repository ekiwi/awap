/**
 * awap_panics.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AGENT_HPP
#define AGENT_HPP

#include <hpp/ostfriesentee.hpp>
#include <jlib_awap-common.hpp>
#include <common.hpp>
#include <message.hpp>
#include "agent_interface.hpp"

namespace awap { class Agent; }
#include <node.hpp>

namespace awap {

class Agent
{
public:
	static Agent* fromPacket(Node& node, uint8_t localId, const uint8_t* content, const size_t length);

	~Agent();

	void setup();
	void timeoutExpired(uint16_t obj) {
		agent.wakeUp(static_cast<int8_t>(obj));
	}

	bool receive(const RxMessage* const msg);

private:
	Agent(Node& node, uint8_t localAgentId, ostfriesentee::Infusion& inf, uint8_t agentClassId, uint8_t* infusionData);

private:
	Node& node;
	uint8_t localAgentId;
	JavaAgentInterface agent;
	ostfriesentee::Infusion infusion;
	uint8_t* infusionData;
	const String name;
};

}
#endif // AGENT_HPP
