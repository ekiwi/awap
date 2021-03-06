/**
 * c-interface.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include <awap/parser.h>
#include <awap/parser.hpp>

#include <vector>
#include <cstring>

// for the C interface, message memory is managed in the library
std::vector<std::unique_ptr<awap::Message>> messages;

// returns negative number on error
int get_service_type_id(const char* service_name)
{
	return awap::Message::getServiceTypeId(std::string(service_name));
}

// returns negative number on error
int get_message_type_id(uint32_t service_id, const char* message_name)
{
	return awap::Message::getMessageTypeId(service_id, std::string(message_name));
}

static inline int insertMessage(std::unique_ptr<awap::Message> msg)
{
	if(msg) {
		// search for empty slot in messages array and return random access id
		int msg_id = 0;
		for(auto& msg_ptr : messages) {
			if(!msg_ptr) {
				msg_ptr = std::move(msg);
				return msg_id;
			}
			++msg_id;
		}
		// if no free slot was found => expand array
		messages.push_back(std::move(msg));
		return msg_id;
	} else {
		return -1;
	}
}

/// returns a message handle on success and less than zero on failure
int message_unmarshal(const uint8_t* data, size_t bytes)
{
	return insertMessage(std::move(awap::Message::unmarshal(data, bytes)));
}

/// returns a message handle on success and less than zero on failure
int message_from_type_id(uint32_t service_id, uint32_t message_id)
{
	return insertMessage(std::move(awap::Message::fromTypeId(service_id, message_id)));
}

static inline bool is_valid_message_handle(int message_handle) {
	return message_handle >= 0 and
	       static_cast<size_t>(message_handle) < messages.size() and
	       messages[message_handle];
}

/// releases a message resource, returns true on success
bool release_message(int message_handle)
{
	if(is_valid_message_handle(message_handle)) {
		messages[message_handle].reset(nullptr);
		return true;
	} else {
		return false;
	}
}

bool message_marshal(int message_handle, uint8_t* output, size_t len)
{
	if(is_valid_message_handle(message_handle)) {
		return messages[message_handle]->marshal(output, len);
	} else {
		return false;
	}
}

#define RETURN_MESSAGE_VALUE(method, default)          \
	if(is_valid_message_handle(message_handle)) {      \
		return messages[message_handle]->method();     \
	} else {                                           \
		return default;                                \
	}

#define SET_MESSAGE_VALUE(method, value)           \
	if(is_valid_message_handle(message_handle)) {  \
		messages[message_handle]->method(value);   \
	}

static bool copy_string(const std::string str, char* output, size_t len)
{
	if(len < str.length()) {
		return false;
	} else {
		std::memcpy(output, str.data(), str.length() + 1);
		return true;
	}
}

#define RETURN_MESSAGE_STRING_VALUE(method)                                   \
	if(is_valid_message_handle(message_handle)) {                             \
		return copy_string(messages[message_handle]->method(), output, len); \
	} else {                                                                  \
		return false;                                                         \
	}

// message access
size_t message_get_size(int message_handle)
{
	RETURN_MESSAGE_VALUE(getSize, 0)
}

int message_get_type_id(int message_handle)
{
	RETURN_MESSAGE_VALUE(getTypeId, -1)
}

int message_get_service_type_id(int message_handle)
{
	RETURN_MESSAGE_VALUE(getServiceTypeId, -1)
}

bool message_get_name(int message_handle, char* output, size_t len)
{
	RETURN_MESSAGE_STRING_VALUE(getName);
}

bool message_get_service_name(int message_handle, char* output, size_t len)
{
	RETURN_MESSAGE_STRING_VALUE(getServiceName);
}

bool message_get_performative(int message_handle, char* output, size_t len)
{
	RETURN_MESSAGE_STRING_VALUE(getPerformative);
}

bool message_is_service_tx_message(int message_handle)
{
	RETURN_MESSAGE_VALUE(isServiceTxMessage, false)
}

bool message_is_broadcast(int message_handle)
{
	RETURN_MESSAGE_VALUE(isBroadcast, false)
}

uint8_t message_get_dest_agent_id(int message_handle)
{
	RETURN_MESSAGE_VALUE(getDestinationAgentId, -1)
}

uint8_t message_get_src_agent_id(int message_handle)
{
	RETURN_MESSAGE_VALUE(getSourceAgentId, -1)
}

void message_set_is_broadcast(int message_handle, bool is_broadcast)
{
	SET_MESSAGE_VALUE(setIsBroadcast, is_broadcast);
}

void message_set_dest_agent_id(int message_handle, uint8_t dest_agent_id)
{
	SET_MESSAGE_VALUE(setDestinationAgentId, dest_agent_id);
}

void message_set_src_agent_id(int message_handle, uint8_t src_agent_id)
{
	SET_MESSAGE_VALUE(setSourceAgentId, src_agent_id);
}

size_t message_get_number_of_fields(int message_handle)
{
	RETURN_MESSAGE_VALUE(getNumberOfFields, 0)
}

// field access
bool message_get_field_name(int message_handle, int field_id, char* output, size_t len)
{
	if(is_valid_message_handle(message_handle)) {
		return copy_string(messages[message_handle]->getFieldName(field_id), output, len);
	} else {
		return false;
	}
}

fieldtype_t message_get_field_type(int message_handle, int field_id)
{
	if(is_valid_message_handle(message_handle)) {
		return static_cast<fieldtype_t>(
			messages[message_handle]->getFieldType(field_id));
	} else {
		return FIELD_TYPE_INVALID;
	}
}

bool message_get_enum_field_string_value(int message_handle, int field_id, char* output, size_t len)
{
	if(is_valid_message_handle(message_handle)) {
		return copy_string(messages[message_handle]->getEnumFieldStringValue(field_id), output, len);
	} else {
		return false;
	}
}

#define RETURN_MESSAGE_FIELD_VALUE(method, default)        \
	if(is_valid_message_handle(message_handle)) {          \
		return messages[message_handle]->method(field_id); \
	} else {                                               \
		return default;                                    \
	}

int64_t message_get_integer_field_value(int message_handle, int field_id)
{
	RETURN_MESSAGE_FIELD_VALUE(getIntegerFieldValue, 0);
}

bool message_get_boolean_field_value(int message_handle, int  field_id)
{
	RETURN_MESSAGE_FIELD_VALUE(getBooleanFieldValue, false);
}

// field write access
int message_get_field_id(int message_handle, const char* field_name)
{
	if(is_valid_message_handle(message_handle)) {
		return messages[message_handle]->getFieldId(std::string(field_name));
	} else {
		return -1;
	}
}

#define SET_MESSAGE_FIELD_VALUE(value)                           \
	if(is_valid_message_handle(message_handle)) {                        \
		return messages[message_handle]->setFieldValue(field_id, value); \
	} else {                                                             \
		return false;                                                    \
	}

bool message_set_enum_field_string_value(int message_handle, int field_id, const char* value)
{
	SET_MESSAGE_FIELD_VALUE(std::string(value));
}

bool message_set_integer_field_value(int message_handle, int field_id, int64_t value)
{
	SET_MESSAGE_FIELD_VALUE(value);
}

bool message_set_boolean_field_value(int message_handle, int field_id, bool value)
{
	SET_MESSAGE_FIELD_VALUE(value);
}
