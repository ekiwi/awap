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

void Runtime::sendBroadcast(const uint8_t* content, const size_t length)
{
	XPCC_LOG_DEBUG << XPCC_FILE_INFO << "trying to send out broadcast packet" << xpcc::endl;
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

void Runtime::registerTimeout(uint32_t milliseconds, uint32_t id)
{
	XPCC_LOG_DEBUG << XPCC_FILE_INFO << "TODO: implement timeout" << xpcc::endl;

}

}
