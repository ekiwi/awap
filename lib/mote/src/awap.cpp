#include <awap.hpp>
#include "agent.hpp"

extern "C"
{
#include <jlib_base.h>
#include <jlib_ostfriesentee.h>
}

#include <hpp/ostfriesentee.hpp>
#include <jlib_awap-common.hpp>

using namespace ostfriesentee;

char * ref_t_base_address;

extern unsigned char di_lib_archive_data[];
extern size_t di_lib_archive_size;

static uint8_t mem[MEMSIZE];
static Vm vm;

static constexpr size_t MaxAgents = 8;
static awap::Agent* agents[MaxAgents];

namespace awap {

template<typename T, size_t N>
static constexpr inline size_t
count(T (&)[N]) { return N; }

void Awap::init(const NodeAddress nodeAddress)
{
	// initialize a new VM
	vm.initialize(mem);
	vm.makeActiveVm();

	// load libraries
	dj_named_native_handler handlers[] = {
			{ "base", &base_native_handler },
			// util does not have any native code
			{ "ostfriesentee", &ostfriesentee_native_handler }
		};

	int length = sizeof(handlers)/ sizeof(handlers[0]);
	dj_archive archive;
	archive.start = (dj_di_pointer)di_lib_archive_data;
	archive.end = (dj_di_pointer)(di_lib_archive_data + di_lib_archive_size);
	vm.loadInfusionArchive(archive, handlers, length);

	// pre-allocate an OutOfMemoryError object
	dj_object* obj = vm.createSysLibObject(BASE_CDEF_java_lang_OutOfMemoryError);
	dj_mem_setPanicExceptionObject(obj);

	// start the main execution loop
	vm.run();
}

void  Awap::receive(const NodeAddress sender, const uint8_t* content, const size_t length)
{
}

void Awap::loadAgent(const uint8_t* content, const size_t length )
{
	for(size_t ii = 0; ii < count(agents); ++ii) {
		if(agents[ii] == nullptr) {
			Agent* agent = Agent::fromPacket(vm, ii, content, length);
			if(agent != nullptr) {
				agents[ii] = agent;
			}
			break;
		}
	}
}

//----------------------------------------------------------------------------
// Darjeeling Functions

extern "C"
void dj_panic(int32_t panictype)
{
	switch(panictype) {
	case DJ_PANIC_OUT_OF_MEMORY:
		return Runtime::panic(Panic::JavaOutOfMemory);
	case DJ_PANIC_ILLEGAL_INTERNAL_STATE:
		return Runtime::panic(Panic::JavaIllegalInternalState);
	case DJ_PANIC_UNIMPLEMENTED_FEATURE:
		return Runtime::panic(Panic::JavaUnimplementedFeature);
	case DJ_PANIC_UNCAUGHT_EXCEPTION:
		return Runtime::panic(Panic::JavaUncaughtException);
	case DJ_PANIC_UNSATISFIED_LINK:
		return Runtime::panic(Panic::JavaUnsatisfiedLink);
	case DJ_PANIC_MALFORMED_INFUSION:
		return Runtime::panic(Panic::JavaMalformedInfusion);
	case DJ_PANIC_ASSERTION_FAILURE:
		return Runtime::panic(Panic::JavaAssertionFailure);
	case DJ_PANIC_SAFE_POINTER_OVERFLOW:
		return Runtime::panic(Panic::JavaSafePointerOverflow);
	default:
		return Runtime::panic(Panic::JavaUnknown);
	}
}

extern "C"
void dj_timer_init(){}

extern "C"
uint32_t dj_timer_getTimeMillis()
{
	return Runtime::getMilliseconds();
}

typedef long ssize_t;

extern "C"
ssize_t write(int /*fildes*/, const void *buf, size_t nbyte)
{
	const char* str = static_cast<const char*>(buf);
	Runtime::write(str, nbyte);
	return nbyte;
}

extern "C"
int debug_printf(const char * format, ...) {
	va_list ap;
	va_start(ap, format);
	Runtime::debugPrintF(format, ap);
	va_end(ap);
	return 0;
}

} // namespace awap
