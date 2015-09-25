/**
 * common.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef COMMON_HPP
#define COMMON_HPP

#include <awap.hpp>

namespace awap {

using ServiceId = uint8_t;
using ServiceTypeId = uint8_t;
using AgentId = uint8_t;

struct RemoteService {
	ServiceTypeId serviceType;
	AgentId agent;
	NodeAddress node;
};

struct LocalService {
	AgentId agent;
	ServiceId service;
};

} // namespace awap

#endif // COMMON_HPP
