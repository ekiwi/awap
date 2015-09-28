/**
 * awap_panics.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AWAP_ERRORS_HPP
#define AWAP_ERRORS_HPP

#include <awap.hpp>

// This headerfile makes it possible to translate awap panic
// and warning codes to strings.

namespace awap {

static inline const char* getPanicDescription(Panic panic)
{
	switch(panic) {
	case Panic::AwapMoteInfusionNotFound:
		return "Awap::init: awap-mote infusion was not found!";
	case Panic::AwapCommonInfusionNotFound:
		return "Awap::init: awap-common infusion was not found!";
	case Panic::NotInitialized:
		return "Awap::init wasn't called first!";
	case Panic::JavaOutOfMemory:
		return "JVM (Ostfriesentee): Out of Memory";
	case Panic::JavaIllegalInternalState:
		return "JVM (Ostfriesentee): Illegal Interal State";
	case Panic::JavaUnimplementedFeature:
		return "JVM (Ostfriesentee): Unimplemented Feature";
	case Panic::JavaUncaughtException:
		return "JVM (Ostfriesentee): Uncaught Exception";
	case Panic::JavaUnsatisfiedLink:
		return "JVM (Ostfriesentee): Unsatisfied Link";
	case Panic::JavaMalformedInfusion:
		return "JVM (Ostfriesentee): Malformed Infusion";
	case Panic::JavaAssertionFailure:
		return "JVM (Ostfriesentee): Assertion Failure";
	case Panic::JavaSafePointerOverflow:
		return "JVM (Ostfriesentee): Safe Pointer Overflow";
	default:
		return "Unknown Panic";
	}
}

static inline const char* getWarningDescription(Warning warn)
{
	switch(warn) {
	case Warning::TimeoutExpiredInvalidAgentId:
		return "Node::timeoutExpired: agent could not found found!";
	default:
		return "Unknown Warning";
	}
}

} // namespace awap

#endif // AWAP_ERRORS_HPP
