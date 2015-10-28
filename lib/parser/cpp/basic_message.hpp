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

class BasicMessage;

class MessageField {
protected:
	MessageField(
		std::weak_ptr<BasicMessage> msg,
		const std::string name, const size_t id)
		: msg(msg), name(name), id(id) {}

public:
	const std::string getName() const {
		return this->name;
	}

	size_t getId() const {
		return this->id;
	}

	virtual FieldType getType() const = 0;

	virtual const std::string getStringValue() const {
		return "";
	}

	virtual bool setValue(const std::string value) {
		return false;
	}

	virtual int64_t getIntegerValue() const {
		return 0;
	}

	virtual bool setValue(int64_t value) {
		return false;
	}

	virtual bool getBooleanValue() const {
		return false;
	}

	virtual bool setValue(bool value) {
		return false;
	}

protected:
	std::weak_ptr<BasicMessage> msg;
	const std::string name;
	const size_t id;
};

class BooleanMessageField : public MessageField {
public:
	BooleanMessageField(
		std::weak_ptr<BasicMessage> msg,
		const std::string name, const size_t id)
		: MessageField(msg, name, id) {}

	bool getBooleanValue() const override {
		return this->value;
	}

	bool setValue(bool value) override {
		this->value = value;
		return true;
	}

private:
	bool value;
};


struct MessageTypeProperties {
	size_t size;
	bool is_service_tx_message;
	uint32_t typeId;
	uint32_t serviceTypeId;
	const std::string serviceName;
	const std::string name;
	const std::string performative;
};

/// provides functionality common to all messages
class BasicMessage : public Message {
public:
	size_t getSize() const override {
		return this->properties.size;
	}

	uint32_t getTypeId() const override {
		return this->properties.typeId;
	}

	uint32_t getServiceTypeId() const override {
		return this->properties.serviceTypeId;
	}

	const std::string getName() const override {
		return this->properties.name;
	}

	const std::string getServiceName() const override {
		return this->properties.serviceName;
	}

	const std::string getPerformative() const override {
		return this->properties.performative;
	}

	bool isServiceTxMessage() const override {
		return this->properties.is_service_tx_message;
	}

	bool isBroadcast() const override {
		return data[0] & (1<<7);
	}

	uint8_t getDestinationAgentId() const override {
		return (data[0] >> 3) & 0x7;
	}

	uint8_t getSourceAgentId() const override {
		return (data[0] >> 0) & 0x7;
	}

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

	int getFieldId(const std::string fieldName) const override {
		for(const auto& field : this->fields) {
			if(field and field->getName() == fieldName) {
				return field->getId();
			}
		}
		return -1; // not found
	}

	bool setFieldValue(size_t fieldId, const std::string value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

	bool setFieldValue(size_t fieldId, int64_t value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

	bool setFieldValue(size_t fieldId, bool value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

private:
	BasicMessage(
		std::unique_ptr<uint8_t []> data,
		const MessageTypeProperties properties)
		: data(std::move(data)), properties(properties) {}

private:
	std::unique_ptr<uint8_t []> data;
	// will be populated by derrived class
	std::vector<std::unique_ptr<MessageField>> fields;
	const MessageTypeProperties properties;

private:
	inline bool isValidFieldId(size_t fieldId) const {
		return fieldId >= 0 and
		       fieldId < this->fields.size();
	}
};


} // namesapce awap

#endif // BASIC_MESSAGE_HPP
