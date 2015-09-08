#include "mote.hpp"
#include <util.hpp>

namespace awap {

Mote::Mote(ostfriesentee::Vm& vm, const NodeAddress nodeAddress)
	: vm(vm), address(nodeAddress)
{}

Mote::~Mote()
{
	for(auto agent : this->agents) {
		if(agent != nullptr) {
			delete agent;
		}
	}
}

void
Mote::loadAgent(const uint8_t* content, const size_t length)
{
	for(size_t ii = 0; ii < arrayCount(agents); ++ii) {
		if(agents[ii] == nullptr) {
			Agent* agent = Agent::fromPacket(vm, ii, content, length);
			if(agent != nullptr) {
				agents[ii] = agent;
			}
			break;
		}
	}
}

void
Mote::receive(const NodeAddress sender, const uint8_t* content, const size_t length)
{
	// TODO!
}

} // namespace awap
