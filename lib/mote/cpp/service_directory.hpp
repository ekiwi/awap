/**
 * service_directory.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef AGENT_DIRECTORY_HPP
#define AGENT_DIRECTORY_HPP

#include <common.hpp>
#include <database.hpp>
#include <util.hpp>

namespace awap {


template<size_t PropDataSize>
struct DirectoryEntry
{
	// not the actual number of properties, but the number of uint32_t values
	// that are necessary to hold all properties
	static constexpr size_t PropertyCount = divideCeil(PropDataSize, sizeof(uint32_t));
	// properties as first member and 32bit wide for alignment reasons
	uint32_t properties[PropertyCount];
	LocalService service;
	ServiceTypeId serviceType;
};

template<size_t PropDataSize>
struct DirectoryQuery
{
	using Entry = DirectoryEntry<PropDataSize>;
	static constexpr size_t PropertyCount = Entry::PropertyCount;
	// properties as first member and 32bit wide for alignment reasons
	uint32_t propertiesMask[PropertyCount];
	uint32_t properties[PropertyCount];
	ServiceId serviceType;

	bool inline match(const Entry& entry) const {
		if(entry.serviceType != serviceType) {
			return false;
		}
		for(size_t ii = 0; ii < PropertyCount; ++ii) {
			const uint32_t mask = propertiesMask[ii];
			const uint32_t masked0 = entry.properties[ii] & mask;
			// TODO: only mask once
			const uint32_t masked1 = properties[ii] & mask;
			if(masked0 != masked1) {
				return false;
			}
		}
		return true;
	}
};

template<size_t PropDataSize>
struct DirectoryRemoveQuery
{
	using Entry = DirectoryEntry<PropDataSize>;
	LocalService service;
	DirectoryRemoveQuery(LocalService service) : service(service) {}
	bool inline match(Entry& e) const {
		return (e.service.agent == service.agent) and
		       (e.service.service == service.service);
	}
};


// simple database that only supports very basic search operations
// currently a fixed size array hold entries that are marked "used"
// if they contain valid data
// insertion and search operations are both O(n)
template<size_t MaxPropDataSize, size_t MaxEntries>
class ServiceDirectory {
public:
	using Entry = DirectoryEntry<MaxPropDataSize>;
	using Query = DirectoryQuery<MaxPropDataSize>;

private:
	using RemoveQuery = DirectoryRemoveQuery<MaxPropDataSize>;
	using DB = Database<Entry, Query, RemoveQuery, MaxEntries>;

public:
	using QueryResult = typename DB::QueryResult;

public:
	// currently there is nothing preventing you from inserting the same
	// service (AgentId, ServiceId) twice
	bool inline insert(Entry entry) {
		return db.insert(entry);
	}

	QueryResult inline find(const Query& query) {
		return db.find(query);
	}

	size_t inline remove(const LocalService service) {
		const RemoveQuery query(service);
		return db.remove(query);
	}

	size_t inline count() {
		return db.count();
	}


private:
	DB db;
};

} // namesapce awap

#endif // AGENT_DIRECTORY_HPP
