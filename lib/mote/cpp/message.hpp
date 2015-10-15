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
	AgentId getDestinationAgent() const { return (content.data[0] >> 3) & 0x7; }
	AgentId getSourceAgent()      const { return (content.data[0] >> 0) & 0x7; }
	ServiceTypeId getServiceType() const { return content.data[1]; }
	virtual bool isServiceTxMessage() const = 0;

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
	size_t marshal(ref_t java_msg, AgentId sourceAgent,
		bool isBroadcast, Slice<uint8_t> output);
	// 2 byte for the common header + data
	size_t inline getSize() const { return 2 + this->getDataSize(); }

	NodeAddress getReceiver() const { return remoteNode; }

protected:
	/// reads from the correct java object type for this message type
	virtual size_t marshalFromSpecificJavaObject(ref_t java_msg, Slice<uint8_t> output) = 0;
	virtual size_t getDataSize() const = 0;

protected:
	NodeAddress remoteNode;
};

} // namespace awap

#endif // MESSAGE_HPP
