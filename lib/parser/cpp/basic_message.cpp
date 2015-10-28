/**
 * basic_message.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "basic_message.hpp"

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


BasicMessage::BasicMessage(std::unique_ptr<uint8_t []> data, size_t length)
	: data(std::move(data)), data_length(length)
{
}

const std::string BasicMessage::getServiceType() const
{
	// TODO: get service type string from generated function
	return "";
}




} // namesapce awap
