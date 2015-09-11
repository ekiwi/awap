#include "agent.hpp"

#include <jlib_awap-common.hpp>
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
Agent::fromPacket(Mote& mote, uint8_t localId, const uint8_t* content, const size_t length)
{
	// right now we assume, that content points to a .di file in memory

	// allocate memory to store infusion
	uint8_t* infusion = new uint8_t[length];
	std::memcpy(infusion, content, length);

	// TODO: decompress compressed infusion

	Infusion inf = mote.getVm().loadInfusion(infusion);

	// try to find the local infusion id of the awap common infusion
	uint8_t awapCommonInfusionId = inf.getLocalInfusionId(mote.getAwapCommon());
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

	ClassDefinition agentClassDef = classes.getElement(agentClassIndex);
	std::cout << "Superclass: " << agentClassDef.getSuperClass() << std::endl;
	std::cout << "Name: " << agentClassDef.getNameId() << std::endl;

	de::rwth_aachen::awap::Agent agent(mote.getAwapCommon(), inf, agentClassIndex);
	// try to construct agent instance


	return new Agent(localId, inf, infusion);
}

Agent::Agent(uint8_t localId, ostfriesentee::Infusion& inf, uint8_t* infusionData)
	: localId(localId), infusion(inf), infusionData(infusionData), name(infusion.getName())
{
	std::cout << "New Agent of Type: " << name << std::endl;
}

Agent::~Agent()
{
	delete this->infusionData;
}

}
