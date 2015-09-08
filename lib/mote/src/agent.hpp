#ifndef AGENT_HPP
#define AGENT_HPP

#include <hpp/ostfriesentee.hpp>

namespace awap {

class Agent
{
public:
	Agent(uint8_t localId, ostfriesentee::Infusion& inf);

private:
	uint8_t localId;
	ostfriesentee::Infusion infusion;
};

}
#endif // AGENT_HPP
