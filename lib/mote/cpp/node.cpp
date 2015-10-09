/**
 * node.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "node.hpp"
#include <util.hpp>
#include <generated/message_parser.hpp>

namespace awap {

Node::Node(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress)
	: vm(vm), awapCommon(awapCommon), awapMote(awapMote), address(nodeAddress)
{
	awap::generated::MessageParserFactory::setAwapCommonInfusion(awapCommon);
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

bool
Node::receive(const NodeAddress sender, Slice<const uint8_t> content)
{
	if(content.length < 2) {
		Runtime::warn(Warning::NodeReceiveMessageTooShort);
		return false;
	}

	// parse message header
	auto header = reinterpret_cast<const CommonMessageHeader*>(content.data);
	auto body = content.sub(2);
	auto parser = generated::MessageParserFactory::getMessageParser(header->serviceType, body);
	if(parser.bytes == 0 || parser.createJava == nullptr) {
		Runtime::warn(Warning::NodeReceiveInvalidMessage);
		return false;
	}

	if(header->isBroadcast) {
		// TODO
	} else {
		if(!validAgent(header->destAgent)) {
			Runtime::warn(Warning::NodeReceiveUnknownAgent);
			return false;
		}
		return agents[header->destAgent]->receive(*header, parser);
	}
}

void
Node::timeoutExpired(uint32_t id)
{
	uint16_t obj  = static_cast<uint16_t>(id & 0xffff);
	AgentId agent = static_cast<uint16_t>((id >> 16) & 0xffff);
	if(check(validAgent(agent), Warning::TimeoutExpiredInvalidAgentId)) {
		agents[agent]->timeoutExpired(obj);
	}
}

void
Node::send(AgentId agent, ref_t message)
{
	// TODO!
}

void
Node::sendBroadcast(AgentId agent, ref_t broadcastMessage)
{
	// TODO!
}

void
Node::requestWakeUp(AgentId agent, uint32_t milliseconds, uint16_t obj)
{
	const uint32_t id = obj | (static_cast<uint32_t>(agent) << 16);
	Runtime::registerTimeout(milliseconds, id);
}

bool
Node::registerService(AgentId agent, ref_t service)
{
	// TODO!
}

bool
Node::deregisterService(AgentId agent, ref_t service)
{
	// TODO!
}

} // namespace awap
