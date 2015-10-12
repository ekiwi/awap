/**
 * message.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef MESSAGE_HPP
#define MESSAGE_HPP

#include <common.hpp>
#include <util.hpp>

namespace awap {

class RxMessage
{
public:
	bool isBroadcast()         const { return content.data[0] & (1<<7); }
	bool isFromRemoteService() const { return content.data[0] & (1<<6); }
	AgentId getDestinationAgent() const { return (content.data[0] >> 3) & 0x7; }
	AgentId getSourceAgent()      const { return (content.data[0] >> 0) & 0x7; }
	ServiceTypeId getServiceType() const { return content.data[1]; }

	ref_t createJavaObject() const;
	// 2 byte for the common header + data
	size_t inline getSize() const { return 2 + this->getDataSize(); }

protected:
	/// creates the correct java object for this type and fills in all data fields
	virtual ref_t createSpecificJavaObject() const = 0;
	virtual size_t getDataSize() const = 0;

public:
	RxMessage(const NodeAddress remoteNode, Slice<const uint8_t> content) :
		remoteNode(remoteNode), content(content) {}

protected:
	const NodeAddress remoteNode;
	Slice<const uint8_t> content;
};

class TxMessage
{
public:
	// returns number of bytes written
	size_t loadFromJavaObject(ref_t msg);
	// 2 byte for the common header + data
	size_t inline getSize() const { return 2 + this->getDataSize(); }

protected:
	/// reads from the correct java object type for this message type
	virtual size_t loadFromSpecificJavaObject(ref_t msg) = 0;
	virtual size_t getDataSize() const = 0;

public:
	TxMessage(const NodeAddress remoteNode, Slice<uint8_t> content) :
		remoteNode(remoteNode), content(content) {}

protected:
	NodeAddress remoteNode;
	Slice<uint8_t> content;
};

} // namespace awap

#endif // MESSAGE_HPP
