#ifndef AGENT_DIRECTORY_HPP
#define AGENT_DIRECTORY_HPP

#include <awap.hpp>
#include <database.hpp>
namespace awap { template<size_t, size_t> class AgentDirectory; }
#include <node.hpp>


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
	// properties as first member and 32bit wide for alignment reasons
	uint32_t properties[PropDataSize];
	uint32_t propertiesMask[PropDataSize];
	ServiceId serviceType;
	// TODO: implement match algorithm
	bool match(const Entry& /*e*/) const { return false; }
};

template<size_t PropDataSize>
struct DirectoryRemoveQuery
{
	using Entry = DirectoryEntry<PropDataSize>;
	LocalService service;
	DirectoryRemoveQuery(LocalService service) : service(service) {}
	bool match(Entry& e) const { return e.service == service; }
};


// simple database that only supports very basic search operations
// currently a fixed size array hold entries that are marked "used"
// if they contain valid data
// insertion and search operations are both O(n)
template<size_t MaxPropDataSize, size_t MaxEntries>
class AgentDirectory {
public:
	using Entry = DirectoryEntry<MaxPropDataSize>;
	using Query = DirectoryQuery<MaxPropDataSize>;

private:
	using RemoveQuery = DirectoryRemoveQuery<MaxPropDataSize>;
	using DB = Database<Entry, Query, RemoveQuery, MaxEntries>;

public:
	using QueryResult = typename DB::QueryResult;

public:
	AgentDirectory() {}
	~AgentDirectory() {};

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
