#ifndef AGENT_DIRECTORY_HPP
#define AGENT_DIRECTORY_HPP


#include <awap.hpp>

namespace awap { template<size_t MaxPropDataSize> class AgentDirectory; }
#include <node.hpp>

namespace awap {


template<size_t PropDataSize>
struct DirectoryEntry
{
	using 
	// properties as first member and 32bit wide for alignment reasons
	uint32_t properties[divideCeil(PropDataSize, sizeof(uint32_t))];
	LocalService service;
	ServiceTypeId serviceType;
	bool used;
};

template<size_t PropDataSize>
struct DirectoryQuery
{
	// properties as first member and 32bit wide for alignment reasons
	uint32_t properties[PropDataSize];
	uint32_t propertiesMask[PropDataSize];
	ServiceId serviceTypeMask;
	ServiceId serviceType;
};


// simple database that only supports very basic search operations
// currently a fixed size array hold entries that are marked "used"
// if they contain valid data
// insertion and search operations are both O(n)
template<size_t MaxPropDataSize, size_t MaxEntries>
class AgentDirectory {
	using Entry = DirectoryEntry<MaxPropDataSize>;
	using Query = DirectoryQuery<MaxPropDataSize>;

public:
	AgentDirectory() {
		for(auto& entry : entries) {
			entry.used = false;
		}
	}


	~AgentDirectory() {};

public:
	// currently there is nothing preventing you from inserting the same
	// service (AgentId, ServiceId) twice
	bool inline insert(DataEntry newEntry) {
		for(auto& entry : entries) {
			if(!entry.used) {
				newEntry.used = true;
				entry = newEntry;
				return true;
			}
		}
	}

	LocalService inline search(

	// has to be called perioically to dispatch messages ... or maybe not ..
	void run() {};

private:
	Entry entries[MaxEntries];

};

} // namesapce awap

#endif // AGENT_DIRECTORY_HPP
