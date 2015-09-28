/**
 * runtime.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include <awap.hpp>
#include <awap_errors.hpp>
#include <xpcc/architecture.hpp>
#include <xpcc/debug/logger.hpp>
#include <xpcc/processing/timer.hpp>
// Set the log level
#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

namespace awap {

void Runtime::send(const NodeAddress receiver,
		const uint8_t* content, const size_t length)
{
	XPCC_LOG_DEBUG << XPCC_FILE_INFO << "trying to send out packet" << xpcc::endl;
}

uint32_t Runtime::getMilliseconds()
{
	return xpcc::Clock::now().getTime();
}

void Runtime::panic(Panic panic)
{
	XPCC_LOG_ERROR << XPCC_FILE_INFO << "Panic: "
		<< getPanicDescription(panic) << xpcc::endl;
	exit(-1);
}

void Runtime::warn(Warning warn)
{
	XPCC_LOG_WARNING << XPCC_FILE_INFO
		<< getWarningDescription(warn) << xpcc::endl;
}

int Runtime::debugPrintF(const char *fmt, va_list args)
{
	XPCC_LOG_DEBUG.printf(fmt, args);
	return 0;
}

void Runtime::write(const char *buf, size_t nbyte)
{
	for(size_t ii = 0; ii < nbyte; ++ii) {
		XPCC_LOG_INFO.write(buf[ii]);
	}
}

struct TimeoutTouple {
	xpcc::Timeout timeout;
	uint32_t data;
	bool used = false;
};

static TimeoutTouple timeouts[100];

void Runtime::registerTimeout(uint32_t milliseconds, uint32_t id)
{
	XPCC_LOG_DEBUG << XPCC_FILE_INFO << "New timeout will expire in "
		<< milliseconds << "ms" << xpcc::endl;
	for(auto& timeout : timeouts) {
		if(!timeout.used) {
			timeout.used = true;
			timeout.data = id;
			timeout.timeout.restart(milliseconds);
			break;
		}
	}
}

// needs to be called periodically
void updateRuntime() {
	// check timeouts
	for(auto& timeout : timeouts) {
		if(timeout.used && timeout.timeout.execute()) {
			XPCC_LOG_DEBUG << XPCC_FILE_INFO << "A timeout expired..." << xpcc::endl;
			Awap::timeoutExpired(timeout.data);
			timeout.used = false;
		}
	}
}

}
