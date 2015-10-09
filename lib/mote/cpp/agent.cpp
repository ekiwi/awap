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
#include <cstring>		// for std::memcpy

// TODO: remove when debuging is done
#include<iostream>

using namespace ostfriesentee;

std::ostream &operator<<(std::ostream &os, dj_local_id const &id) {
	os << "(" << static_cast<uint32_t>(id.infusion_id)
	   << ", " << static_cast<uint32_t>(id.entity_id) << ")";
	return os;
}

std::ostream &operator<<(std::ostream &os, String const &str) {
	os.write(str.data, str.length);
	return os;
}

std::ostream &operator<<(std::ostream &os, awap::String const &str) {
	os.write(str.data, str.length);
	return os;
}

namespace awap {


Agent*
Agent::fromPacket(Node& node, uint8_t localId, const uint8_t* content, const size_t length)
{
	// right now we assume, that content points to a .di file in memory

	// allocate memory to store infusion
	uint8_t* infusion = new uint8_t[length];
	std::memcpy(infusion, content, length);

	// TODO: decompress compressed infusion

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
	if(agentClassIndex == -1) return nullptr;


	//de::rwth_aachen::awap::Agent agent(node.getAwapCommon(), inf, agentClassIndex);

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
	std::cout << "New Agent of Type: " << name << std::endl;

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
Agent::receive(const CommonMessageHeader& header, const MessageParser& parser)
{
	return false;
}

Agent::~Agent()
{
	delete this->infusionData;
}

}
