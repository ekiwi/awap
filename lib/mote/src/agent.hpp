#ifndef AGENT_HPP
#define AGENT_HPP

#include <hpp/ostfriesentee.hpp>

namespace awap {

class Agent
{
public:
	static Agent* fromPacket(ostfriesentee::Vm& vm, uint8_t localId, const uint8_t* content, const size_t length);

private:
	Agent(uint8_t localId, ostfriesentee::Infusion& inf);

private:
	uint8_t localId;
	ostfriesentee::Infusion infusion;
};

}
#endif // AGENT_HPP
