/**
 * awap.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
*/

#ifndef AWAP_HPP
#define AWAP_HPP

#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>	// va_list

// This headerfile defines the C++ interface to the awap mote runtime.

namespace awap {

using NodeAddress = uint16_t;

enum class Panic {
	NotInitialized,	// Awap::init wasn't called first
	// Ostfriesentee Errors
	JavaOutOfMemory,
	JavaIllegalInternalState,
	JavaUnimplementedFeature,
	JavaUncaughtException,
	JavaUnsatisfiedLink,
	JavaMalformedInfusion,
	JavaAssertionFailure,
	JavaSafePointerOverflow,
	JavaUnknown,
};

//----------------------------------------------------------------------------
// class that implements methofs that need to be called by the runtime
//----------------------------------------------------------------------------
class Awap {
public:
	/// first method that needs to be called to initialize the library
	static void init(const NodeAddress nodeAddress);

	/// needs to be called, when a new packet was received
	static void receive(const NodeAddress sender,
			const uint8_t* content, const size_t length);

	/// for testing: load an agent
	static void loadAgent(const uint8_t* content, const size_t length);
};


//----------------------------------------------------------------------------
// class that needs to be implemented by the runtime
//----------------------------------------------------------------------------
class Runtime {
public:
	/// called by awap to dispatch a packet
	/// `content` points to an internal memory buffer that remains valid,
	/// until the function returns
	static void send(const NodeAddress receiver,
			const uint8_t* content, const size_t length);

	/// called by awap to a timestamp in milliseconds
	/// this does not have to be the current time, just deltas have to be correct
	static uint32_t getMilliseconds();

	/// called by awap if a fatal, unrecoverable failure happens
	static void panic(Panic panic);

	/// called by awap for debug output
	static int debugPrintF(const char *fmt, va_list args);

	/// write characters to standard output
	static void write(const char *buf, size_t nbyte);
};

} // namespace awap

#endif // AWAP_HPP
