/**
 * awap.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
*/

#ifndef AWAP_HPP
#define AWAP_HPP

extern "C" {
#include <awap.h>
}
#include "slice.hpp"

namespace awap {

using NodeAddress = uint16_t;

class Awap {
	static void init(const NodeAddress nodeAddress);
	static void receive(const NodeAddress sender, const Slice<const uint8_t>& content);

public:
	static inline void send(const NodeAddress receiver, const Slice<const uint8_t>& content) {
		awap_send_packet(static_cast<awap_address_t>(receiver), content.data, content.length);
	}
};

} // namespace awap

#endif // AWAP_HPP
