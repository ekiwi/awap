#ifndef AGENT_DIRECTORY_HPP
#define AGENT_DIRECTORY_HPP

#include <xpcc/container/dynamic_array.hpp>
using namespace xpcc;

#include <awap.hpp>

namespace awap { template<size_t MaxPropDataSize> class AgentDirectory; }
#include <mote.hpp>

namespace awap {

using service_id_t = uint8_t;


template<size_t PropDataSize>
struct DirectoryEntry
{
	uint8_t moteIndex;
	uint8_t agentId;
	service_id_t serviceId;
	uint8_t properties[PropDataSize];
};

template<size_t PropDataSize>
struct DirectoryQuery
{
	service_id_t serviceIdMask;
	service_id_t serviceId;
	uint8_t properties[PropDataSize];
	uint8_t propertiesMask[PropDataSize];
};

struct MoteData
{
	uint8_t dbIndex;
	NodeAddress address;
	uint8_t versionNumber;	// this is incremented everytime a change is made
	uint8_t latestVersionCounter;	// called `c` in trickle paper
};




template<size_t MaxPropDataSize>
class AgentDirectory {
	using Entry = DirectoryEntry<MaxPropDataSize>;
	using Query = DirectoryQuery<MaxPropDataSize>;

public:
	AgentDirectory() {};
	~AgentDirectory() {};

	// has to be called perioically to dispatch messages ... or maybe not ..
	void run() {};

private:
	DynamicArray<Entry> entries;

};

} // namesapce awap

#endif // AGENT_DIRECTORY_HPP
