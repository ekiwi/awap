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
#include <xpcc/container/queue.hpp>
// Set the log level
#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

namespace awap {

struct Packet {
	NodeAddress sender;
	const uint8_t* content;
	size_t length;
};

xpcc::BoundedQueue<Packet, 10> packets;

static inline void addPacket(const NodeAddress sender,
	const uint8_t* content, const size_t length)
{
	// copy content
	auto content_copy = new uint8_t[length];
	std::memcpy(content_copy, content, length);
	packets.push({0, content_copy, length});
}

void Runtime::send(const NodeAddress receiver,
		const uint8_t* content, const size_t length)
{
	// XPCC_LOG_DEBUG << XPCC_FILE_INFO << "trying to send out packet" << xpcc::endl;
	if(receiver == 0) {
		XPCC_LOG_WARNING << XPCC_FILE_INFO << "echoing packet back to node, TODO: remove" << xpcc::endl;
		addPacket(0, content, length);
	}
}

void Runtime::sendBroadcast(const uint8_t* content, const size_t length)
{
	// XPCC_LOG_DEBUG   << XPCC_FILE_INFO << "trying to send out broadcast packet" << xpcc::endl;
	XPCC_LOG_WARNING << XPCC_FILE_INFO << "echoing broadcast back to node, TODO: remove" << xpcc::endl;
	addPacket(0, content, length);
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
	// XPCC_LOG_DEBUG << XPCC_FILE_INFO << "New timeout will expire in "
	//	<< milliseconds << "ms" << xpcc::endl;
	for(auto& timeout : timeouts) {
		if(!timeout.used) {
			timeout.used = true;
			timeout.data = id;
			timeout.timeout.restart(milliseconds);
			break;
		}
	}
}

void Runtime::setActorValue(int32_t value) {
	XPCC_LOG_DEBUG << "setActorValue(" << value << ")" << xpcc::endl;
}

int32_t Runtime::getSensorValue() {
	return 123;
}

// needs to be called periodically
void updateRuntime() {
	// check timeouts
	for(auto& timeout : timeouts) {
		if(timeout.used && timeout.timeout.execute()) {
			// XPCC_LOG_DEBUG << XPCC_FILE_INFO << "A timeout expired..." << xpcc::endl;
			Awap::timeoutExpired(timeout.data);
			timeout.used = false;
		}
	}

	// check packets
	while(!packets.isEmpty()) {
		const auto packet = packets.get();
		packets.pop();
		Awap::receive(packet.sender, packet.content, packet.length);
		delete [] packet.content;
	}
}

}
