#include "agent.hpp"

#include <cstring>		// for std::memcpy

// TODO: remove when debuging is done
#include<iostream>

using namespace ostfriesentee;

std::ostream &operator<<(std::ostream &os, dj_local_id const &id) {
	os << "(" << static_cast<uint32_t>(id.infusion_id)
	   << ", " << static_cast<uint32_t>(id.entity_id) << ")";
	return os;
}

std::ostream &operator<<(std::ostream &os, String const &str) {
	os.write(str.data, str.length);
	return os;
}

namespace awap {


Agent*
Agent::fromPacket(Vm& vm, uint8_t localId, const uint8_t* content, const size_t length)
{
	// right now we assume, that content points to a .di file in memory

	// allocate memory to store infusion
	uint8_t* infusion = new uint8_t[length];
	std::memcpy(infusion, content, length);

	// TODO: decompress compressed infusion

	Infusion inf = vm.loadInfusion(infusion);
	return new Agent(localId, inf, infusion);
}

Agent::Agent(uint8_t localId, ostfriesentee::Infusion& inf, uint8_t* infusionData)
	: localId(localId), infusion(inf), infusionData(infusionData)
{
	// try to inspect infusion
	std::cout << std::endl << "Infusion: " << infusion.getName() << std::endl;
	ClassList classes = infusion.getClassList();
	std::cout << "Number of classes: " << static_cast<int>(classes.getSize()) << std::endl;
	for(uint8_t ii = 0; ii < classes.getSize(); ++ii) {
		ClassDefinition def = classes.getElement(ii);
		int numberOfInterfaces = def.getNumberOfInterfaces();
		std::cout << "Superclass: " << def.getSuperClass() << std::endl;
		std::cout << "Name: " << def.getNameId() << std::endl;
		std::cout << "Interfaces: " << numberOfInterfaces << std::endl;
	}

	List methods = infusion.getMethodImplementationList();
	std::cout << "Number of methods: " << static_cast<int>(methods.getSize()) << std::endl;


	StringTable strings = infusion.getStringTable();
	std::cout << "Number of strings: " << static_cast<int>(strings.getSize()) << std::endl;
	for(uint16_t ii = 0; ii < strings.getSize(); ++ii) {
		std::cout << strings.getString(ii) << std::endl;
	}
}

Agent::~Agent()
{
	delete this->infusionData;
}

}
