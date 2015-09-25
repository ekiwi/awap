/**
 * message_handler.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#ifndef MESSAGE_HANDLER_HPP
#define MESSAGE_HANDLER_HPP

#include "node.hpp"

namespace awap {

class MessageHandler
{

public:
	MessageHandler(Node& node);
	~MessageHandler();

	void receive(const NodeAddress sender, const uint8_t* content, const size_t length);


private:
	Node& node;

};

} // namespace awap

#endif // MESSAGE_HANDLER_HPP
