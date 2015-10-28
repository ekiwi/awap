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
std::unique_ptr<Message> Message::fromPacket(const uint8_t* data, size_t length)
{
	if(length < 3) {
		return nullptr;
	}
	// TODO: determine which message this is and create derrived BaseMessage
	//       instance accordingly
	return nullptr;
}

/// returns emptr unique_ptr on error, check for nullptr!
std::unique_ptr<Message> Message::fromTypeId(uint32_t serviceId, uint32_t messageId)
{
	// TODO: determine which message this is and create derrived BaseMessage
	//       instance accordingly
	return nullptr;
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

BasicMessage::BasicMessage(std::unique_ptr<uint8_t []> data, size_t size)
	: data(std::move(data)), size(size)
{
}

const std::string BasicMessage::getServiceType() const
{
	// TODO: get service type string from generated function
	return "";
}




} // namesapce awap
