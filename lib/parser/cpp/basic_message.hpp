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
protected:
	MessageField(const std::string name, const size_t id)
		: name(name), id(id) {}

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

private:
	const std::string name;
	const size_t id;
};

/// provides functionality common to all messages
class BasicMessage : public Message {
public:
	size_t getSize() const override {
		return this->size;
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

	bool setEnumFieldStringValue(size_t fieldId, const std::string value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

	bool setIntegerFieldValue(size_t fieldId, int64_t value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

	bool setBooleanFieldValue(size_t fieldId, bool value) override {
		if(isValidFieldId(fieldId)) {
			return this->fields[fieldId]->setValue(value);
		} else {
			return false;
		}
	}

private:
	BasicMessage(std::unique_ptr<uint8_t []> data, size_t size);

private:
	std::unique_ptr<uint8_t []> data;
	size_t size;
	// will be populated by derrived class
	std::vector<std::unique_ptr<MessageField>> fields;
	// can be changed by derrived class in constructor
	bool is_service_tx_message = false;

private:
	inline bool isValidFieldId(size_t fieldId) const {
		return fieldId >= 0 and
		       fieldId < this->fields.size();
	}
};


} // namesapce awap

#endif // BASIC_MESSAGE_HPP
