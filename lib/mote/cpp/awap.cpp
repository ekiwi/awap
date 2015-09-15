#include <awap.hpp>
#include "common.hpp"
#include "mote.hpp"

extern "C"
{
#include <jlib_base.h>
#include <jlib_ostfriesentee.h>
#include <jlib_awap-mote.h>
#include "array.h"
}

#include <hpp/ostfriesentee.hpp>

#include <cstring> // std::strcmp

using namespace ostfriesentee;

char * ref_t_base_address;

extern unsigned char di_lib_archive_data[];
extern size_t di_lib_archive_size;

static uint8_t mem[MEMSIZE];
static Vm vm;
static awap::Mote* mote = nullptr;

static const char* AwapCommonInfusionName = "awap-common";
static const char* AwapMoteInfusionName = "awap-mote";

namespace awap {

void Awap::init(const NodeAddress nodeAddress)
{
	// initialize a new VM
	vm.initialize(mem);
	vm.makeActiveVm();

	// load libraries
	dj_named_native_handler handlers[] = {
			{ "base", &base_native_handler },
			// util does not have any native code
			{ "ostfriesentee", &ostfriesentee_native_handler },
			// awap-common does not have any native code
			{ "awap-mote", &awap_mote_native_handler }
		};

	dj_archive archive;
	archive.start = (dj_di_pointer)di_lib_archive_data;
	archive.end = (dj_di_pointer)(di_lib_archive_data + di_lib_archive_size);
	vm.loadInfusionArchive(archive, handlers, arrayCount(handlers));

	// pre-allocate an OutOfMemoryError object
	dj_object* obj = vm.createSysLibObject(BASE_CDEF_java_lang_OutOfMemoryError);
	dj_mem_setPanicExceptionObject(obj);

	// start the main execution loop
	vm.run();

	// find awap-common infusion
	auto inf = vm.firstInfusion();
	ostfriesentee::Infusion awapCommonInf(nullptr), awapMoteInf(nullptr);
	while(inf.isValid()) {
		if(std::strcmp(inf.getName(), AwapCommonInfusionName) == 0) {
			awapCommonInf = inf;
		} else if(std::strcmp(inf.getName(), AwapMoteInfusionName) == 0) {
			awapMoteInf = inf;
		}
		inf = inf.next();
	}
	if(!awapCommonInf.isValid()) Runtime::panic(Panic::AwapCommonInfusionNotFound);
	if(!awapMoteInf.isValid()) Runtime::panic(Panic::AwapMoteInfusionNotFound);

	// create mote instance
	mote = new Mote(vm, awapCommonInf, awapMoteInf, nodeAddress);
}

void  Awap::receive(const NodeAddress sender, const uint8_t* content, const size_t length)
{
	if(mote == nullptr) Runtime::panic(Panic::NotInitialized);
	mote->receive(sender, content, length);
}

void Awap::loadAgent(const uint8_t* content, const size_t length )
{
	if(mote == nullptr) Runtime::panic(Panic::NotInitialized);
	mote->loadAgent(content, length);
}

//----------------------------------------------------------------------------
// awap-mote infusion native functions
extern "C"
int debug_printf(const char * format, ...);

// void de.rwth_aachen.awap.mote.Mote.send(int, de.rwth_aachen.awap.Message)
extern "C"
void de_rwth_aachen_awap_mote_Mote_void_send_int_de_rwth_aachen_awap_Message()
{
	uint8_t agentId = static_cast<uint8_t>(dj_exec_stackPopInt());
	ref_t message = dj_exec_stackPopRef();
	debug_printf("TODO: implement Mote.send method.\n");
}

// boolean de.rwth_aachen.awap.mote.Mote.deregisterService(int, de.rwth_aachen.awap.LocalService)
extern "C"
void de_rwth_aachen_awap_mote_Mote_boolean_deregisterService_int_de_rwth_aachen_awap_LocalService()
{
	uint8_t agentId = static_cast<uint8_t>(dj_exec_stackPopInt());
	ref_t service = dj_exec_stackPopRef();
	debug_printf("TODO: implement Mote.deregisterService method.\n");
	dj_exec_stackPushShort(static_cast<uint16_t>(true));
}

// byte de.rwth_aachen.awap.mote.Mote.installServiceListener(int, de.rwth_aachen.awap.Agent, int, de.rwth_aachen.awap.ServiceProperty[])
extern "C"
void de_rwth_aachen_awap_mote_Mote_byte_installServiceListener_int_de_rwth_aachen_awap_Agent_int_de_rwth_aachen_awap_ServiceProperty__()
{
	uint8_t agentId = static_cast<uint8_t>(dj_exec_stackPopInt());
	uint8_t serviceTypeId = static_cast<uint8_t>(dj_exec_stackPopInt());
	ref_t listener = dj_exec_stackPopRef();
	dj_array* properties = reinterpret_cast<dj_array*>(REF_TO_VOIDP(dj_exec_stackPopRef()));
	debug_printf("TODO: implement Mote.installServiceListener method.\n");
	dj_exec_stackPushShort(0);
}

// boolean de.rwth_aachen.awap.mote.Mote.registerService(int, de.rwth_aachen.awap.LocalService)
extern "C"
void de_rwth_aachen_awap_mote_Mote_boolean_registerService_int_de_rwth_aachen_awap_LocalService()
{
	uint8_t agentId = static_cast<uint8_t>(dj_exec_stackPopInt());
	ref_t service = dj_exec_stackPopRef();
	debug_printf("TODO: implement Mote.registerService method.\n");
	dj_exec_stackPushShort(static_cast<uint16_t>(true));
}

// boolean de.rwth_aachen.awap.mote.Mote.uninstallServiceListener(int, byte)
extern "C"
void de_rwth_aachen_awap_mote_Mote_boolean_uninstallServiceListener_int_byte()
{
	uint8_t agentId = static_cast<uint8_t>(dj_exec_stackPopInt());
	uint8_t localServiceId = static_cast<uint8_t>(dj_exec_stackPopInt());
	debug_printf("TODO: implement Mote.uninstallServiceListener method.\n");
	dj_exec_stackPushShort(static_cast<uint16_t>(true));
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