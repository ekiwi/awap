#ifndef COMMON_HPP
#define COMMON_HPP

#include <awap.hpp>
#include <util.hpp>
#include <generated/configuration.hpp>

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
