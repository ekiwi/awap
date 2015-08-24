#include <awap.hpp>

extern "C"
{
#include "jlib_base.h"
#include "jlib_ostfriesentee.h"
}

#include <hpp/ostfriesentee.hpp>

using namespace ostfriesentee;

extern unsigned char di_lib_archive_data[];
extern size_t di_lib_archive_size;

uint8_t mem[MEMSIZE];

namespace awap {

void Awap::init(const NodeAddress nodeAddress)
{
	// initialise memory manager
	dj_mem_init(mem, MEMSIZE);
	ref_t_base_address = (char*)mem - 42;

	// Create a new VM
	Vm vm;
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

} // namespace awap
