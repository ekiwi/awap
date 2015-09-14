#ifndef MOTE_HPP
#define MOTE_HPP

#include <hpp/ostfriesentee.hpp>
#include <awap.hpp>

namespace awap { class Mote; }
#include <agent.hpp>

namespace awap {

class Mote
{
public:
	static constexpr size_t MaxAgents = 8;

public:
	Mote(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress);
	~Mote();

	void loadAgent(const uint8_t* content, const size_t length);
	void receive(const NodeAddress sender, const uint8_t* content, const size_t length);

	inline ostfriesentee::Vm& getVm() { return this->vm; }
	inline ostfriesentee::Infusion& getAwapCommon() { return this->awapCommon; }
	inline ostfriesentee::Infusion& getAwapMote()   { return this->awapMote; }

private:
	Agent* agents[MaxAgents] = { nullptr };
	ostfriesentee::Vm& vm;
	ostfriesentee::Infusion awapCommon;
	ostfriesentee::Infusion awapMote;
	const NodeAddress address;
	uint8_t awapCommonInfusionId;
};

}
#endif // MOTE_HPP
