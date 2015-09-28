/**
 * main.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include <awap.hpp>
#include <xpcc/architecture.hpp>
#include <xpcc/debug/logger.hpp>

// Set the log level
#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

using namespace awap;

extern unsigned char di_temperature_agent_data[];
extern size_t di_temperature_agent_size;
extern unsigned char di_consumer_agent_data[];
extern size_t di_consumer_agent_size;

int main() {
	XPCC_LOG_INFO << XPCC_FILE_INFO << "Awap Mote Runtime" << xpcc::endl;

	Awap::init(0);
	Awap::loadAgent(di_temperature_agent_data, di_temperature_agent_size);
	Awap::loadAgent(di_consumer_agent_data, di_consumer_agent_size);

	return 0;
}
