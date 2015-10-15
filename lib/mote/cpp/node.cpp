/**
 * node.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "node.hpp"
#include <util.hpp>
#include <generated/messages.hpp>
#include <generated/service_descriptions.hpp>

namespace awap {

Node::Node(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress)
	: vm(vm), awapCommon(awapCommon), awapMote(awapMote), address(nodeAddress)
{
	awap::generated::MessageFactory::setAwapCommonInfusion(awapCommon);
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

	const auto msg = generated::MessageFactory::makeRxMessage(sender, content);
	if(msg == nullptr) {
		Runtime::warn(Warning::NodeReceiveInvalidMessage);
		return false;
	}

	if(msg->isBroadcast()) {
		return receiveBroadcast(msg, content.sub(msg->getSize()));
	} else {
		const auto destAgent = msg->getDestinationAgent();
		if(!validAgent(destAgent)) {
			Runtime::warn(Warning::NodeReceiveUnknownAgent);
			return false;
		}
		return agents[destAgent]->receive(msg);
	}
}

bool
Node::receiveBroadcast(RxMessage* msg, Slice<const uint8_t> broadcast_content)
{
	using SD = awap::generated::ServiceDescription;

	const auto serviceType = msg->getServiceType();
	const size_t propSize = SD::getPropertySize(serviceType);
	if(broadcast_content.length < 1 + propSize) {
		Runtime::warn(Warning::NodeReceiveBroadcastMessageTooShort);
		return false;
	}

	Services::Query query;
	query.serviceType = serviceType;
	const auto broadcastHeader = broadcast_content.data[0];
	SD::toQueryMask(serviceType, broadcastHeader, slice(query.propertiesMask));
	auto properties = reinterpret_cast<uint8_t *>(query.properties);
	std::memcpy(properties, &broadcast_content.data[1], propSize);

	auto result = this->services.find(query);
	bool success = true;
	for(auto entry : result) {
		auto destAgent = entry.service.agent;
		if(!validAgent(destAgent)) {
			Runtime::warn(Warning::NodeReceiveBroadcastUnknownAgentFromDB);
			return false;
		}
		success = success and agents[destAgent]->receive(msg);
	}
	return success;
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
	auto txMessage = generated::MessageFactory::makeTxMessage(message);

	const size_t msgSize = txMessage->getSize();
	auto output = slice(new uint8_t[msgSize], msgSize);
	if(txMessage->marshal(message, agent, false, output) != msgSize) {
		delete output.data;
		return; // error!!
	}

	Runtime::send(txMessage->getReceiver(), output.data, msgSize);

	delete output.data;
}

void
Node::sendBroadcast(AgentId agent, ref_t broadcastMessage)
{
	using SD = awap::generated::ServiceDescription;
	using BroadcastMessage =
		_AWAP_COMMON_STRUCT_de_rwth_aachen_awap_BroadcastMessage;


	auto broadcast_data =
		reinterpret_cast<BroadcastMessage*>(REF_TO_VOIDP(broadcastMessage));
	auto txMessage = generated::MessageFactory::makeTxMessage(broadcast_data->msg);

	const size_t msgSize = txMessage->getSize();
	// 1 byte for broadcast header
	const size_t maxPacketSize = msgSize + 1 + MaxPropBytes;
	// TODO: should use a unique_ptr, but is there support on embedded?
	auto output = slice(new uint8_t[maxPacketSize], maxPacketSize);

	if(txMessage->marshal(broadcast_data->msg, agent, true, output) != msgSize) {
		delete output.data;
		return; // error!!
	}
	output.data[msgSize] = SD::toBroadcastHeader(broadcast_data->recipients);
	const size_t descriptionSize =
		SD::marshal(broadcast_data->recipients, output.sub(msgSize + 1));

	const size_t packetSize = msgSize + 1 + descriptionSize;
	Runtime::sendBroadcast(output.data, packetSize);

	delete output.data;
}

void
Node::requestWakeUp(AgentId agent, uint32_t milliseconds, uint16_t obj)
{
	const uint32_t id = obj | (static_cast<uint32_t>(agent) << 16);
	Runtime::registerTimeout(milliseconds, id);
}

bool
Node::registerService(AgentId agent, ServiceId localServiceId, ref_t description)
{
	using SD = awap::generated::ServiceDescription;

	Services::Entry entry;
	entry.service.agent = agent;
	entry.service.service = localServiceId;
	entry.serviceType = SD::getServiceTypeId(description);
	SD::marshal(description, slice(entry.properties));

	return this->services.insert(entry);
}

bool
Node::deregisterService(AgentId agent, ServiceId localServiceId)
{
	LocalService service;
	service.agent = agent;
	service.service = localServiceId;

	return (this->services.remove(service) > 0);
}

} // namespace awap
