#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#include<common.hpp>

namespace awap {

struct CommonMessageHeader {
	bool isBroadcast          : 1;
	bool isFromRemoteService  : 1;
	AgentId destAgent         : 3;
	AgentId srcAgent          : 3;
	ServiceTypeId serviceType : 8;
} __attribute__((packed));

static_assert(sizeof(CommonMessageHeader) == 2, "sizeof(CommonMessageHeader) needs to be 2 bytes!");

//struct ReceiveEnvelope {
//	AgentId localAgent;
//	ServiceId localService;
//	Message msg;
//	
//};

} // namespace awap

#endif // MESSAGE_HPP
