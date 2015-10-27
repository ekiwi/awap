/**
 * awap/parser.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AWAP_PARSER_HPP
#define AWAP_PARSER_HPP

#include <stdint.h>
#include <stddef.h>
#include <memory>

// This headerfile defines the C++ interface to the awap message parser

namespace awap {

enum class FieldType {
	Invalid = 0,	///< returned for invalid field ids
	Enum = 1,
	Boolean = 2,
	Int = 3,
};

class Message {
	bool isBroadcast() const;
	uint8_t getDestinationAgentId() const;
	uint8_t getSourceAgentId() const;
	uint8_t getServiceTypeId() const;
	std::string&& getServiceType() const;
	bool isServiceTxMessage() const;

	size_t getNumberOfFields() const;
	std::string&& getFieldName(size_t fieldId) const;
	FieldType getFieldType(size_t fieldId) const;
	std::string&& getEnumFieldStringValue(size_t fieldId) const;
	uint64_t getEnumFieldIntegerValue(size_t fieldId) const;
	int64_t getIntegerFieldValue(size_t fieldId) const;
	bool getBooleanFieldValue(size_t fieldId) const;
};

/// returns emptr unique_ptr on error, check for nullptr!
std::unique_ptr<Message> parseMessage(uint8_t* data, size_t bytes);

} // namesapce awap

#endif // AWAP_PARSER_HPP
