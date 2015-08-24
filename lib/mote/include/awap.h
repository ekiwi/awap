/**
 * awap.h
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
*/
#ifndef AWAP_H
#define AWAP_H

// This headerfile defines the C interface to the awap mote runtime.
#include <stdint.h>
#include <stddef.h>


typedef uint16_t awap_address_t;

typedef enum {
	AWAP_ERROR_JAVA_OUT_OF_MEMORY,
	AWAP_ERROR_JAVA_ILLEGAL_INTERNAL_STATE,
	AWAP_ERROR_JAVA_UNIMPLEMENTED_FEATURE,
	AWAP_ERROR_JAVA_UNCAUGHT_EXCEPTION,
	AWAP_ERROR_JAVA_UNSATISFIED_LINK,
	AWAP_ERROR_JAVA_MALFORMED_INFUSION,
	AWAP_ERROR_JAVA_ASSERTION_FAILURE,
	AWAP_ERROR_JAVA_SAFE_POINTER_OVERFLOW,
} awap_error_t;

//----------------------------------------------------------------------------
// Functions that need to be called by the underlying system
//----------------------------------------------------------------------------

/// first method that needs to be called to initialize the library
void awap_init(const awap_address_t node_address);

/// needs to be called, when a new packet was received
void awap_receive_packet(const awap_address_t sender,
		const uint8_t* content, const size_t length);

//----------------------------------------------------------------------------
// Functions that need to be implemented by the underlying system
//----------------------------------------------------------------------------

/// called by awap to dispatch a packet
/// `content` points to an internal memory buffer that remains valid,
/// until the function returns
void awap_send_packet(const awap_address_t receiver,
		const uint8_t* content, const size_t length);

/// called by awap to a timestamp in milliseconds
/// this does not have to be the current time, just deltas have to be correct
uint32_t awap_get_milliseconds();

/// called by awap if a fatal, unrecoverable failure happens
void awap_panic(awap_error_t error);

#endif // AWAP_H
