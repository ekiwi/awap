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

#include "../../../../ext/xpcc/examples/stm32f072_discovery/stm32f072_discovery.hpp"

// Set the log level
#undef	XPCC_LOG_LEVEL
#define	XPCC_LOG_LEVEL xpcc::log::DEBUG

// Create an IODeviceWrapper around the Uart Peripheral we want to use
xpcc::IODeviceWrapper< Usart1, xpcc::IOBuffer::BlockIfFull > loggerDevice;

// Set all four logger streams to use the UART
xpcc::log::Logger xpcc::log::debug(loggerDevice);
xpcc::log::Logger xpcc::log::info(loggerDevice);
xpcc::log::Logger xpcc::log::warning(loggerDevice);
xpcc::log::Logger xpcc::log::error(loggerDevice);

// Dummy Clock
struct DummyClock {
	static constexpr int Usart1 = 8 * 1000 * 1000;
};


using namespace awap;

extern unsigned char di_temperature_agent_data[];
extern size_t di_temperature_agent_size;
extern unsigned char di_consumer_agent_data[];
extern size_t di_consumer_agent_size;

namespace awap {
void updateRuntime();
}

int main() {
	// initialize Uart1 for XPCC_LOG_
	GpioOutputA9::connect(Usart1::Tx);
	GpioInputA10::connect(Usart1::Rx, Gpio::InputType::PullUp);
	Usart1::initialize<DummyClock, 115200>(12);

	XPCC_LOG_INFO << XPCC_FILE_INFO << "Awap Mote Runtime" << xpcc::endl;

	Awap::init(0);
	Awap::loadAgent(di_temperature_agent_data, di_temperature_agent_size);
	Awap::loadAgent(di_consumer_agent_data, di_consumer_agent_size);

	while(true) {
		awap::updateRuntime();
		// sleep(1);
	}

	return 0;
}
