#ifndef MOTE_HPP
#define MOTE_HPP

#include <hpp/ostfriesentee.hpp>
#include <agent.hpp>
#include <awap.hpp>

namespace awap {

class Mote
{
public:
	static constexpr size_t MaxAgents = 8;

public:
	Mote(ostfriesentee::Vm& vm, const NodeAddress nodeAddress);
	~Mote();

	void loadAgent(const uint8_t* content, const size_t length);
	void receive(const NodeAddress sender, const uint8_t* content, const size_t length);

private:
	Agent* agents[MaxAgents] = { nullptr };
	ostfriesentee::Vm& vm;
	const NodeAddress address;
};

}
#endif // MOTE_HPP
