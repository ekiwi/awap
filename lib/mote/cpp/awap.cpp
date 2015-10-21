/**
 * awap.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include <awap.hpp>
#include "common.hpp"
#include "node.hpp"

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

static uint8_t __attribute__((aligned(4))) mem[MEMSIZE];
static Vm vm;
static awap::Node* node = nullptr;

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
	// since we have only loaded libraries, that do not contain a main
	// function, this will run the static constructors only
	vm.run();

	// find awap-common and awap-mote infusion
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

	// create node instance
	node = new Node(vm, awapCommonInf, awapMoteInf, nodeAddress);
}

void Awap::deinit()
{
	assert(node != nullptr, Panic::NotInitialized);
	delete node;
}

void  Awap::receive(const NodeAddress sender, const uint8_t* content, const size_t length)
{
	assert(node != nullptr, Panic::NotInitialized);
	node->receive(sender, Slice<const uint8_t>(content, length));
}

void Awap::loadAgent(const uint8_t* content, const size_t length )
{
	assert(node != nullptr, Panic::NotInitialized);
	node->loadAgent(content, length);
}

void Awap::timeoutExpired(uint32_t id)
{
	assert(node != nullptr, Panic::NotInitialized);
	node->timeoutExpired(id);
}

//----------------------------------------------------------------------------
// internal interface
ostfriesentee::Infusion& getAwapCommonInfusion() {
	assert(node != nullptr, Panic::NotInitialized);
	return node->getAwapCommon();
}
//----------------------------------------------------------------------------
// awap-mote infusion native functions
extern "C"
int debug_printf(const char * format, ...);

/// resolves the "this" reference to the NodeAdapter and
/// reads out the id of the assosiated agent
static inline uint8_t retriveAgentId()
{
	// we assume,.that all reference arguments have been poped and
	// thus the next item on the reference stack is the "this" reference
	const auto adapter_ptr = REF_TO_VOIDP(dj_exec_stackPeekRef());
	const auto adapter =
		static_cast<_AWAP_MOTE_STRUCT_de_rwth_aachen_awap_mote_NodeAdapter*>(adapter_ptr);
	return static_cast<uint8_t>(adapter->agentId);
}

// void de.rwth_aachen.awap.mote.NodeAdapter.send(de.rwth_aachen.awap.Message)
extern "C"
void de_rwth_aachen_awap_mote_NodeAdapter_void_send_de_rwth_aachen_awap_Message()
{
	assert(node != nullptr, Panic::NotInitialized);
	ref_t message = dj_exec_stackPopRef();
	node->send(retriveAgentId(), message);
}

// void de.rwth_aachen.awap.mote.NodeAdapter.send(de.rwth_aachen.awap.BroadcastMessage)
extern "C"
void de_rwth_aachen_awap_mote_NodeAdapter_void_send_de_rwth_aachen_awap_BroadcastMessage()
{
	assert(node != nullptr, Panic::NotInitialized);
	ref_t message = dj_exec_stackPopRef();
	node->sendBroadcast(retriveAgentId(), message);
}

// void de.rwth_aachen.awap.mote.NodeAdapter.requestWakeUp(int, java.lang.Object)
extern "C"
void de_rwth_aachen_awap_mote_NodeAdapter_void_requestWakeUp_int_byte()
{
	assert(node != nullptr, Panic::NotInitialized);
	uint16_t obj = dj_exec_stackPopShort();
	uint32_t milliseconds = dj_exec_stackPopInt();
	node->requestWakeUp(retriveAgentId(), milliseconds, obj);
}

// boolean de.rwth_aachen.awap.mote.NodeAdapter.registerService(int, de.rwth_aachen.awap.ServiceDescription)
extern "C"
void de_rwth_aachen_awap_mote_NodeAdapter_boolean_registerService_int_de_rwth_aachen_awap_ServiceDescription()
{
	assert(node != nullptr, Panic::NotInitialized);
	int localServiceId = dj_exec_stackPopInt();
	ref_t description = dj_exec_stackPopRef();
	bool ret = node->registerService(retriveAgentId(), localServiceId, description);
	dj_exec_stackPushShort(static_cast<uint16_t>(ret));
}

// boolean de.rwth_aachen.awap.mote.NodeAdapter.deregisterService(int)
extern "C"
void de_rwth_aachen_awap_mote_NodeAdapter_boolean_deregisterService_int()
{
	assert(node != nullptr, Panic::NotInitialized);
	int localServiceId = dj_exec_stackPopInt();
	bool ret = node->deregisterService(retriveAgentId(), localServiceId);
	dj_exec_stackPushShort(static_cast<uint16_t>(ret));
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
