/**
 * message.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "message.hpp"
#include <hpp/ostfriesentee.hpp>
#include <jlib_awap-common.hpp>

namespace awap {

using MessageStruct = de::rwth_aachen::awap::Message::UnderlyingType;
using RemoteAgentStruct = de::rwth_aachen::awap::RemoteAgent::UnderlyingType;


ref_t RxMessage::createJavaObject() const {
	auto msg = this->createSpecificJavaObject();
	if(msg == 0) {
		return 0;
	}
	// fill in common fields
	auto common = reinterpret_cast<MessageStruct*>(REF_TO_VOIDP(msg));
	common->serviceTypeId = this->getServiceType();
	common->remoteAgentId =
		static_cast<uint32_t>(this->getSourceAgent()) << 16 |
		static_cast<uint32_t>(this->remoteNode);
	return msg;
}


size_t TxMessage::loadFromJavaObject(ref_t msg) {
	if(this->content.length < 2) {
		return 0;
	}
	// load common fields
	auto common = reinterpret_cast<MessageStruct*>(REF_TO_VOIDP(msg));
	this->content.data[1] = static_cast<uint8_t>(common->serviceTypeId);
	this->content.data[0] |= (static_cast<uint32_t>(common->remoteAgentId) >> 16) & 0x7;
	this->remoteNode    =  static_cast<uint32_t>(common->remoteAgentId) & 0xffff;

	// load specific fields
	return this->loadFromSpecificJavaObject(msg) + 2;
}

} // namespace awap
