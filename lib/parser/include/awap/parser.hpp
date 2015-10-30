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
	Integer = 3,
};

class Message {
public:
	/// returns emptr unique_ptr on error, check for nullptr!
	static std::unique_ptr<Message> unmarshal(const uint8_t* data, size_t length);
	static std::unique_ptr<Message> fromTypeId(uint32_t serviceId, uint32_t messageId);

	// returns negative number on error
	static int getServiceTypeId(const std::string serviceName);
	// returns negative number on error
	static int getMessageTypeId(uint32_t serviceId, const std::string messageName);

public:
	virtual bool marshal(uint8_t* output, size_t len) const = 0;

	// static data, specific to message tye
	virtual size_t getSize() const = 0;
	virtual uint32_t getTypeId() const = 0;
	virtual uint32_t getServiceTypeId() const = 0;
	virtual const std::string getName() const = 0;
	virtual const std::string getServiceName() const = 0;
	virtual const std::string getPerformative() const = 0;
	virtual bool isServiceTxMessage() const = 0;

	// data that can change in each individual message
	virtual bool isBroadcast() const = 0;
	virtual void setIsBroadcast(bool isBroadcast) = 0;
	virtual uint8_t getDestinationAgentId() const = 0;
	virtual void setDestinationAgentId(uint8_t destinationAgentId) = 0;
	virtual uint8_t getSourceAgentId() const = 0;
	virtual void setSourceAgentId(uint8_t sourceAgentId) = 0;

	virtual size_t getNumberOfFields() const = 0;
	virtual const std::string getFieldName(size_t fieldId) const = 0;
	virtual FieldType getFieldType(size_t fieldId) const = 0;
	virtual const std::string getEnumFieldStringValue(size_t fieldId) const = 0;
	virtual int64_t getIntegerFieldValue(size_t fieldId) const = 0;
	virtual bool getBooleanFieldValue(size_t fieldId) const = 0;

	virtual int getFieldId(const std::string fieldName) const = 0;
	virtual bool setFieldValue(size_t fieldId, const std::string value) = 0;
	virtual bool setFieldValue(size_t fieldId, int64_t value) = 0;
	virtual bool setFieldValue(size_t fieldId, bool value) = 0;

public:
	virtual ~Message(){}
};


} // namesapce awap

#endif // AWAP_PARSER_HPP
