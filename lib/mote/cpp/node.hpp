#ifndef NODE_HPP
#define NODE_HPP

#include <hpp/ostfriesentee.hpp>
#include <awap.hpp>

namespace awap { class Node; }
#include <agent.hpp>

namespace awap {

class Node
{
public:
	static constexpr size_t MaxAgents = 8;

public:
	Node(ostfriesentee::Vm& vm, ostfriesentee::Infusion& awapCommon, ostfriesentee::Infusion& awapMote, const NodeAddress nodeAddress);
	~Node();

	void loadAgent(const uint8_t* content, const size_t length);
	void receive(const NodeAddress sender, const uint8_t* content, const size_t length);

//	bool receiveRemoteServiceMessage(const uint8_t agentId, , ref_t messageObject)



//	bool receivePacket(const uint8_t agentId, const bool remoteService, ref_t messageObject)
//	{
//		if(agentId >= MaxAgents || agents[agentId] == nullptr) {
//			return false;
//		} else {
//			return agents[agentId]->receivePacket(remoteService, messageObject);
//		}
//	}

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
#endif // NODE_HPP