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
#include <initializer_list>

namespace awap {

class BasicMessage;

class MessageField {
protected:
	MessageField(
		const std::string name)
		: name(name) {}

public:
	virtual ~MessageField() {}

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

	virtual bool setValue(const std::string /* value */) {
		return false;
	}

	virtual int64_t getIntegerValue() const {
		return 0;
	}

	virtual bool setValue(int64_t /* value */) {
		return false;
	}

	virtual bool getBooleanValue() const {
		return false;
	}

	virtual bool setValue(bool /* value */) {
		return false;
	}

public:
	void setParentMessage(BasicMessage* msg) {
		this->msg = msg;
	}

	void setId(size_t id) {
		this->id = id;
	}

protected:
	BasicMessage* msg;
	const std::string name;
	size_t id;
};

class BooleanMessageField : public MessageField {
public:
	BooleanMessageField(const std::string name)
		: MessageField(name) {}

	bool getBooleanValue() const override {
		return this->value;
	}

	bool setValue(bool value) override {
		this->value = value;
		return true;
	}

	int64_t getIntegerValue() const override {
		return this->value? 1 : 0;
	}

	FieldType getType() const override {
		return FieldType::Boolean;
	}

private:
	bool value;
};


class IntegerMessageField : public MessageField {
public:
	IntegerMessageField(
			const std::string name,
			int64_t minValue, int64_t maxValue)
		: MessageField(name),
		minValue(minValue),
		maxValue(std::max(minValue, maxValue)),
		value(minValue) {}

	int64_t getIntegerValue() const override {
		return this->value;
	}

	bool setValue(int64_t value) override {
		if(value >= minValue and value <= maxValue) {
			this->value = value;
			return true;
		} else {
			return false;
		}
	}

	FieldType getType() const override {
		return FieldType::Integer;
	}

private:
	const int64_t minValue;
	const int64_t maxValue;
protected:
	int64_t value;
};

class Marshaller;

struct MessageTypeProperties {
	MessageTypeProperties(
		const std::string serviceName,
		const std::string name,
		const std::string performative) :
		serviceName(serviceName),
		name(name), performative(performative) {}
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
	BasicMessage(
		const MessageTypeProperties properties,
		std::unique_ptr<Marshaller> marshaller,
		// should be unique_ptr<MessageField>, because ownership is moved...
		std::initializer_list<MessageField*> msg_fields)
		: properties(properties), marshaller(std::move(marshaller))
	{
		for(auto& field : msg_fields) {
			field->setParentMessage(this);
			field->setId(this->fields.size());
			this->fields.emplace_back(field);
		}
	}

	BasicMessage(
		const MessageTypeProperties properties,
		std::unique_ptr<Marshaller> marshaller)
		: properties(properties), marshaller(std::move(marshaller)) {}

public:
	bool unmarshal(const uint8_t* input, size_t len);

	bool marshal(uint8_t* output, size_t len) const override;

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
		return data0 & (1<<7);
	}

	void setIsBroadcast(bool isBroadcast) override {
		if(isBroadcast) {
			data0 |= (1<<7);
		} else {
			data0 &= ~(1<<7);
		}
	}

	uint8_t getDestinationAgentId() const override {
		return (data0 >> 3) & 0x7;
	}

	void setDestinationAgentId(uint8_t destinationAgentId) override {
		data0 = (data0 & ~(0x7 << 3)) | ((destinationAgentId & 0x07) << 3);
	}

	uint8_t getSourceAgentId() const override {
		return (data0 >> 0) & 0x7;
	}

	void setSourceAgentId(uint8_t sourceAgentId) override {
		data0 = (data0 & ~(0x7)) | (sourceAgentId & 0x07);
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
	std::vector<std::unique_ptr<MessageField>> fields;
	const MessageTypeProperties properties;
	uint8_t data0 = 0;
	std::unique_ptr<Marshaller> marshaller;

	friend class Marshaller;

private:
	inline bool isValidFieldId(size_t fieldId) const {
		return fieldId < this->fields.size();
	}
};

class Marshaller {
protected:
	virtual bool unmarshalSpecific(BasicMessage* msg, const uint8_t* input) const = 0;
	virtual bool marshalSpecific(const BasicMessage* msg, uint8_t* output) const = 0;
public:
	bool unmarshal(BasicMessage* msg, const uint8_t* input, size_t len) const {
		if(len < msg->getSize()) {
			return false;
		} else {
			msg->data0 = input[0];
			return this->unmarshalSpecific(msg, &input[2]);
		}
	}

	bool marshal(const BasicMessage* msg, uint8_t* output, size_t len) const {
		if(len < msg->getSize()) {
			return false;
		} else {
			output[0] = msg->data0;
			output[1] = msg->properties.serviceTypeId;
			return this->marshalSpecific(msg, &output[2]);
		}
	}
};

} // namesapce awap

#endif // BASIC_MESSAGE_HPP
