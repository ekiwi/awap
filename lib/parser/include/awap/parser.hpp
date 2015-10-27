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
public:
	/// returns emptr unique_ptr on error, check for nullptr!
	static std::unique_ptr<Message> fromPacket(const uint8_t* data, size_t length);

public:
	virtual bool isBroadcast() const = 0;
	virtual uint8_t getDestinationAgentId() const = 0;
	virtual uint8_t getSourceAgentId() const = 0;
	virtual uint8_t getServiceTypeId() const = 0;
	virtual bool isServiceTxMessage() const = 0;
	virtual const std::string getServiceType() const = 0;

	virtual size_t getNumberOfFields() const = 0;
	virtual const std::string getFieldName(size_t fieldId) const = 0;
	virtual FieldType getFieldType(size_t fieldId) const = 0;
	virtual const std::string getEnumFieldStringValue(size_t fieldId) const = 0;
	virtual uint64_t getEnumFieldIntegerValue(size_t fieldId) const = 0;
	virtual int64_t getIntegerFieldValue(size_t fieldId) const = 0;
	virtual bool getBooleanFieldValue(size_t fieldId) const = 0;
};


} // namesapce awap

#endif // AWAP_PARSER_HPP
