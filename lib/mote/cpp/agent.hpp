#ifndef AGENT_HPP
#define AGENT_HPP

#include <hpp/ostfriesentee.hpp>
#include <jlib_awap-common.hpp>
#include <common.hpp>

namespace awap { class Agent; }
#include <mote.hpp>

namespace awap {

class Agent
{
public:
	static Agent* fromPacket(Mote& mote, uint8_t localId, const uint8_t* content, const size_t length);

	~Agent();

	void setup();

private:
	Agent(Mote& mote, uint8_t localAgentId, ostfriesentee::Infusion& inf, uint8_t agentClassId, uint8_t* infusionData);

private:
	Mote& mote;
	uint8_t localAgentId;
	::de::rwth_aachen::awap::Agent agent;
	ostfriesentee::Infusion infusion;
	uint8_t* infusionData;
	const String name;
};

}
#endif // AGENT_HPP
