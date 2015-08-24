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

int Runtime::debugPrintF(const char* format, ...)
{
	va_list ap;
	va_start(ap, format);
	vprintf(format, ap);
	va_end(ap);
	return 0;
}

}
