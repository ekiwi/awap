#ifndef AGENT_DIRECTORY_HPP
#define AGENT_DIRECTORY_HPP


#include <awap.hpp>

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
public:
	using Entry = DirectoryEntry<MaxPropDataSize>;
	using Query = DirectoryQuery<MaxPropDataSize>;


	AgentDirectory() {}
	~AgentDirectory() {};

public:
	// currently there is nothing preventing you from inserting the same
	// service (AgentId, ServiceId) twice
	bool inline insert(Entry newEntry) {
		for(auto& entry : entries) {
			if(!entry.used) {
				entry = newEntry;
				entry.used = true;
				return true;
			}
		}
		return false;
	}

	// LocalService inline search(


private:
	struct InternalEntry : public Entry{
		bool used;
		InternalEntry() : Entry(), used(false) {}

		/// assignment to place Entry in InternalEntry
		InternalEntry& operator=(const Entry& other) {
			// TODO: this is extremely ugly and potentialle not performant
			for(size_t ii = 0; ii < Entry::PropertyCount; ++ii) {
				this->properties[ii] = other.properties[ii];
			}
			this->service = other.service;
			this->serviceType = other.serviceType;
			this->used = true;
			return *this;
		}
	};
	InternalEntry entries[MaxEntries];

};

} // namesapce awap

#endif // AGENT_DIRECTORY_HPP
