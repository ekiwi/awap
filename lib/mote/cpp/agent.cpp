/**
 * agent.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include "agent.hpp"

#include <jlib_awap-common.hpp>
#include <jlib_awap-mote.hpp>

#if defined(AGENT_COMPRESSION_ENABLED)
	#include <huffman.hpp>
#else // !defined(AGENT_COMPRESSION_ENABLED)
	#include <cstring>		// for std::memcpy
#endif

using namespace ostfriesentee;


namespace awap {

Agent*
Agent::fromPacket(Node& node, uint8_t localId, const uint8_t* content, const size_t length)
{
#if defined(AGENT_COMPRESSION_ENABLED)
	auto input = slice(content, length);

	// allocate memory to store infusion
	if(input.length < 3) { return nullptr; }

	uint16_t agent_size = static_cast<uint16_t>(input.data[0]) << 8 | input.data[1];
	assert(agent_size <= 1000, Panic::AgentSizeLarger1KiB);

	uint8_t* infusion = new uint8_t[agent_size];
	assert(infusion != nullptr, Panic::LoadingAgentOutOfMemory);

	// decompress
	Slice<uint8_t> output(infusion, agent_size);
	bool success = huffman::decode(input.sub(2), output);
	assert(success, Panic::LoadingAgentFailedToDecompress);

#else // !defined(AGENT_COMPRESSION_ENABLED)
	assert(length <= 1000, Panic::AgentSizeLarger1KiB);
	uint8_t* infusion = new uint8_t[length];
	assert(infusion != nullptr, Panic::LoadingAgentOutOfMemory);
	std::memcpy(infusion, content, length);
#endif

	Infusion inf = node.getVm().loadInfusion(infusion);

	// try to find the local infusion id of the awap common infusion
	uint8_t awapCommonInfusionId = inf.getLocalInfusionId(node.getAwapCommon());
	if(awapCommonInfusionId == 0) return nullptr;

	// try to find class that inherits from awap agent
	// we will assume that there is only one such class in one infusion
	ClassList classes = inf.getClassList();
	int agentClassIndex = -1;
	for(uint8_t ii = 0; ii < classes.getSize(); ++ii) {
		ClassDefinition def = classes.getElement(ii);
		auto superclass = def.getSuperClass();
		if(superclass.infusion_id == 0) {
			// TODO: follow
		} else if(superclass.infusion_id == awapCommonInfusionId) {
			if(superclass.entity_id == de::rwth_aachen::awap::Agent::ClassId) {
				agentClassIndex = ii;
				break;
			}
		}
	}

	if(agentClassIndex == -1) {
		return nullptr;
	}


	return new Agent(node, localId, inf, agentClassIndex, infusion);
}

Agent::Agent(Node& node, uint8_t localAgentId, ostfriesentee::Infusion& inf, uint8_t agentClassId, uint8_t* infusionData)
	: node(node),
	localAgentId(localAgentId),
	agent(node.getAwapCommon(), inf, agentClassId),
	infusion(inf),
	infusionData(infusionData),
	name(infusion.getName())
{
	// construct node adapter by calling
	// de.rwth_aachen.awap.mote.NodeAdapter.initializeAgent
	int16_t intParams[2];
	ref_t refParams[1];
	ostfriesentee::Object::setParam(intParams, 0, static_cast<int32_t>(localAgentId));
	ostfriesentee::Object::setParam(refParams, 0, agent.getRef());
	static constexpr uint8_t initializeAgentMethodId =
		AWAP_MOTE_MIMPL_de_rwth_aachen_awap_mote_NodeAdapter_void_initializeAgent_de_rwth_aachen_awap_Agent_int;
	ostfriesentee::Object::runMethod(node.getAwapMote(), initializeAgentMethodId, refParams, intParams);
}

void
Agent::setup()
{
	agent.setup();
}

bool
Agent::receive(std::unique_ptr<const RxMessage> msg)
{
	// if message was transmitted from a remote service
	if(msg->isServiceTxMessage()) {
		return agent.handleRemoteServiceMessage(node.getAwapCommon(), std::move(msg));
	} else {
		auto java_msg = msg->createJavaObject();
		if(java_msg == 0) {
			return false;
		} else {
			agent.handleLocalServiceMessage(java_msg);
			return true;
		}
	}
}

Agent::~Agent()
{
	delete this->infusionData;
}

}
