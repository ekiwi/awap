#include <awap.hpp>
#include <iostream>

using namespace awap;

extern unsigned char di_temperature_agent_data[];
extern size_t di_temperature_agent_size;
extern unsigned char di_subscriber_agent_data[];
extern size_t di_subscriber_agent_size;

int main() {
	std::cout << "Awap Mote Runtime" << std::endl;

	Awap::init(0);
	Awap::loadAgent(di_temperature_agent_data, di_temperature_agent_size);
	Awap::loadAgent(di_subscriber_agent_data, di_subscriber_agent_size);

	return 0;
}
