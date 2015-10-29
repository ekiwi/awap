/**
 * awap/parser.h
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AWAP_PARSER_H
#define AWAP_PARSER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

// This headerfile defines the C interface to the awap message parser


typedef enum {
	FIELD_TYPE_INVALID = 0,
	FIELD_TYPE_ENUM = 1,
	FIELD_TYPE_BOOLEAN = 2,
	FIELD_TYPE_INT = 3,
} fieldtype_t;


// returns negative number on error
int get_service_type_id(const char* service_name);
// returns negative number on error
int get_message_type_id(uint32_t service_id, const char* message_name);

/// returns a message handle on success and less than zero on failure
int message_from_packet(const uint8_t* data, size_t bytes);

/// returns a message handle on success and less than zero on failure
int message_from_type_id(uint32_t service_id, uint32_t message_id);

/// releases a message resource, returns true on success
bool release_message(int message_handle);

// message access
size_t message_get_size(int message_handle);
bool message_is_broadcast(int message_handle);
int message_get_dest_agent_id(int message_handle);
int message_get_src_agent_id(int message_handle);
int message_get_service_type_id(int message_handle);
bool message_get_service_type(int message_handle, char* output, size_t len);
bool message_is_service_tx_message(int message_handle);
size_t message_get_number_of_fields(int message_handle);

// field read access
bool message_get_field_name(int message_handle, int field_id, char* output, size_t len);
fieldtype_t message_get_field_type(int message_handle, int field_id);
bool message_get_enum_field_string_value(int message_handle, int field_id, char* output, size_t len);
int64_t message_get_integer_field_value(int message_handle, int field_id);
bool message_get_boolean_field_value(int message_handle, int field_id);

// field write access
int message_get_field_id(int message_handle, const char * field_name);
bool message_set_enum_field_string_value(int message_handle, int field_id, const char* value);
bool message_set_integer_field_value(int message_handle, int field_id, int64_t value);
bool message_set_boolean_field_value(int message_handle, int field_id, bool value);

#ifdef __cplusplus
}
#endif

#endif // AWAP_PARSER_H
