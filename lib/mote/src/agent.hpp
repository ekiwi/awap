#ifndef AGENT_HPP
#define AGENT_HPP

#include <hpp/ostfriesentee.hpp>
#include <common.hpp>

namespace awap { class Agent; }
#include <mote.hpp>

namespace awap {

class Agent
{
public:
	static Agent* fromPacket(Mote& mote, uint8_t localId, const uint8_t* content, const size_t length);

	~Agent();

private:
	Agent(uint8_t localId, ostfriesentee::Infusion& inf, uint8_t* infusionData);

private:
	uint8_t localId;
	ostfriesentee::Infusion infusion;
	uint8_t* infusionData;
	const String name;
};

}
#endif // AGENT_HPP
