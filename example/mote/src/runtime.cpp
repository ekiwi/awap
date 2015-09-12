#include <awap.hpp>
#include <awap_panics.hpp>
#include <iostream>
#include <time.h>
#include <stdarg.h>

namespace awap {

void Runtime::send(const NodeAddress receiver,
		const uint8_t* content, const size_t length)
{
	std::cout << "trying to send out packet" << std::endl;
}

uint32_t Runtime::getMilliseconds()
{
	return clock() / (CLOCKS_PER_SEC / 1000);
}

void Runtime::panic(Panic panic)
{
	std::cout << "Panic: " << getPanicDescription(panic) << std::endl;
	exit(-1);
}

int Runtime::debugPrintF(const char *fmt, va_list args)
{
	vprintf(fmt, args);
	return 0;
}

void Runtime::write(const char *buf, size_t nbyte)
{
	std::cout.write(buf, nbyte);
}

}
