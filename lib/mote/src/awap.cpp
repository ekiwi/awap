#include "awap.hpp"

extern "C"
void awap_init(const awap_address_t node_address) {
	return awap::Awap::init(static_cast<awap::NodeAddress>(node_address));
}

extern "C"
void awap_receive_packet(const awap_address_t sender,
		const uint8_t* content, const size_t length) {
	return awap::Awap::receive(static_cast<awap::NodeAddress>(sender), awap::slice(content, length));
}



namespace awap {



} // namespace awap
