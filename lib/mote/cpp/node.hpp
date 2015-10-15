/**
 * node.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef NODE_HPP
#define NODE_HPP

#include <hpp/ostfriesentee.hpp>
#include <common.hpp>
#include <service_directory.hpp>
#include <util.hpp>
#include <generated/configuration.hpp>

namespace awap { class Node; }
#include <agent.hpp>

namespace awap {

class Node
{
public:
	static constexpr size_t MaxAgents = 8;
	static constexpr size_t MaxServices = 16;

public:
	Node(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress);
	~Node();

	void loadAgent(const uint8_t* content, const size_t length);
	bool receive(const NodeAddress sender, Slice<const uint8_t> content);
	void timeoutExpired(uint32_t id);

	// node interface methods
	void send(AgentId agent, ref_t message);
	void sendBroadcast(AgentId agent, ref_t broadcastMessage);
	// TODO: keep obj in java and only hand index to c++
	void requestWakeUp(AgentId agent, uint32_t milliseconds, uint16_t obj);
	bool registerService(AgentId agent, ServiceId localServiceId, ref_t description);
	bool deregisterService(AgentId agent, ServiceId localServiceId);

private:
	bool receiveBroadcast(RxMessage* msg, Slice<const uint8_t> broadcast_content);

public:
	inline ostfriesentee::Vm& getVm() { return this->vm; }
	inline ostfriesentee::Infusion& getAwapCommon() { return this->awapCommon; }
	inline ostfriesentee::Infusion& getAwapMote()   { return this->awapMote; }

	inline bool validAgent(AgentId id) {
		return (id < MaxAgents) && (agents[id] != nullptr);
	}
private:
	Agent* agents[MaxAgents] = { nullptr };
	ostfriesentee::Vm& vm;
	ostfriesentee::Infusion awapCommon;
	ostfriesentee::Infusion awapMote;
	const NodeAddress address;
	static constexpr size_t MaxPropBytes =
		divideCeil(generated::Configuration::MaxPropertyBitCount, 8u);
	using Services = ServiceDirectory<MaxPropBytes, MaxServices>;
	Services services;
};

}
#endif // NODE_HPP
