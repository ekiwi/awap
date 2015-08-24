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

// This headerfile defines the C++ interface to the awap mote runtime.

namespace awap {

using NodeAddress = uint16_t;

enum class Error {
	JavaOutOfMemory,
	JavaIllegalInternalState,
	JavaUnimplementedFeature,
	JavaUncaughtException,
	JavaUnsatisfiedLink,
	JavaMalformedInfusion,
	JavaAssertionFailure,
	JavaSagePointerOverflow,
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
	static void panic(Error error);
};

} // namespace awap

#endif // AWAP_HPP
