/**
 * basic_message.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "basic_message.hpp"
#include <generated/messages.hpp>

namespace awap {

/// returns emptr unique_ptr on error, check for nullptr!
std::unique_ptr<Message> Message::unmarshal(const uint8_t* data, size_t length)
{
	if(length < 3) {
		return nullptr;
	}
	return awap::generated::unmarshal(data, length);
}

/// returns emptr unique_ptr on error, check for nullptr!
std::unique_ptr<Message> Message::fromTypeId(uint32_t serviceId, uint32_t messageId)
{
	return awap::generated::messageFromTypeId(serviceId, messageId);
}

// returns negative number on error
int Message::getServiceTypeId(const std::string serviceName)
{
	return generated::getServiceTypeId(serviceName);
}

// returns negative number on error
int Message::getMessageTypeId(uint32_t serviceId, const std::string messageName)
{
	return generated::getMessageTypeId(serviceId, messageName);
}

bool BasicMessage::unmarshal(const uint8_t* input, size_t len) {
	if(this->marshaller) {
		return this->marshaller->unmarshal(this, input, len);
	} else {
		return false;
	}
}

bool BasicMessage::marshal(uint8_t* output, size_t len) const {
	if(this->marshaller) {
		return this->marshaller->marshal(this, output, len);
	} else {
		return false;
	}
}

} // namesapce awap
