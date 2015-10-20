/**
 * agent_interface.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AGENT_INTERFACE_HPP
#define AGENT_INTERFACE_HPP

#include <hpp/ostfriesentee.hpp>
#include <jlib_awap-common.hpp>
#include <memory>

namespace awap {

/// class that extends the interface to the agent java class
class JavaAgentInterface : public ::de::rwth_aachen::awap::Agent {
public:
	using ::de::rwth_aachen::awap::Agent::Agent;

	// uses the onReceive methods defined by the IServiceNameListener
	// to dispatch a message from a remote servie to this agent
	bool inline handleRemoteServiceMessage(ostfriesentee::Infusion& awapCommon, std::unique_ptr<const RxMessage> msg) {
		auto java_msg = msg->createJavaObject();
		if(java_msg == 0) {
			return false;
		} else {
			// arguments are the this pointer and the reference to the java_msg
			ref_t refParams[2];
			setParam(refParams, 0, this->obj);
			setParam(refParams, 1, java_msg);
			dj_mem_addSafeReference(&refParams[0]);
			dj_mem_addSafeReference(&refParams[1]);
			// the definition of the correct onReceive method can be found in the awap common infusion
			dj_global_id onReceiveDefinitionId {
				awapCommon.getUnderlying(),
				msg->getOnReceiveMethodDefinitionId()
			};
			// lookup the method implementation for this Agent instance
			dj_global_id method =
				dj_global_id_lookupVirtualMethod(onReceiveDefinitionId, this->obj);
			// prepare the stack frame
			dj_exec_callMethodFromNative(method, getThread(), &refParams[1], nullptr);
			// TODO: run untill method finished
			dj_exec_run(100000);
			dj_mem_removeSafeReference(&refParams[0]);
			dj_mem_removeSafeReference(&refParams[1]);
		}
		return true;
	}

};

} // namespace awap

#endif // AGENT_INTERFACE_HPP
