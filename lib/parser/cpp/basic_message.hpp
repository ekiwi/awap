/**
 * basic_message.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef BASIC_MESSAGE_HPP
#define BASIC_MESSAGE_HPP

#include <awap/parser.hpp>
#include <vector>

namespace awap {


class MessageField {
public:
	const std::string getName() const {
		return this->name;
	}

	virtual FieldType getType() const = 0;

	virtual const std::string getStringValue() const {
		return "";
	}

	virtual int64_t getIntegerValue() const {
		return 0;
	}

	virtual bool getBooleanValue() const {
		return false;
	}

private:
	std::string name;
};

/// provides functionality common to all messages
class BasicMessage : public Message {
public:
	bool isBroadcast() const override {
		return data[0] & (1<<7);
	}

	uint8_t getDestinationAgentId() const override {
		return (data[0] >> 3) & 0x7;
	}

	uint8_t getSourceAgentId() const override {
		return (data[0] >> 0) & 0x7;
	}

	uint8_t getServiceTypeId() const override {
		return data[1];
	}

	bool isServiceTxMessage() const override {
		return is_service_tx_message;
	}

	const std::string getServiceType() const override;

	size_t getNumberOfFields() const override {
		return this->fields.size();
	}

	const std::string getFieldName(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->getName();
		} else {
			return "";
		}
	}

	FieldType getFieldType(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->getType();
		} else {
			return FieldType::Invalid;
		}
	}

	const std::string getEnumFieldStringValue(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->getStringValue();
		} else {
			return "";
		}
	}

	uint64_t getEnumFieldIntegerValue(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return static_cast<uint64_t>(this->fields[fieldId]->getIntegerValue());
		} else {
			return 0;
		}
	}

	int64_t getIntegerFieldValue(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->getIntegerValue();
		} else {
			return 0;
		}
	}

	bool getBooleanFieldValue(size_t fieldId) const override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->getBooleanValue();
		} else {
			return false;
		}
	}

private:
	BasicMessage(std::unique_ptr<uint8_t []> data, size_t length);

private:
	std::unique_ptr<uint8_t []> data;
	size_t data_length;
	// will be populated by derrived class
	std::vector<std::unique_ptr<MessageField>> fields;
	// can be changed by derrived class in constructor
	bool is_service_tx_message = false;

private:
	inline bool isValidFieldId(size_t fieldId) const {
		return fieldId < this->fields.size();
	}
};


} // namesapce awap

#endif // BASIC_MESSAGE_HPP
