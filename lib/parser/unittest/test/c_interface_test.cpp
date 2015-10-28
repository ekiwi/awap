/**
 * c_interface_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "c_interface_test.hpp"
#include <awap/parser.h>

void
CInterfaceTest::testGetTypeId()
{
	TEST_ASSERT_EQUALS(get_service_type_id("MessageTestService"), 0);
	TEST_ASSERT_EQUALS(get_service_type_id("RoomService"), 3);
	TEST_ASSERT_EQUALS(get_service_type_id("EnergySupplyService"), 7);

	TEST_ASSERT_EQUALS(get_message_type_id(0, "EmptyMessage"), 0);
	TEST_ASSERT_EQUALS(get_message_type_id(0, "SimpleUInt32Message"), 1);
	TEST_ASSERT_EQUALS(get_message_type_id(0, "SimpleUInt12Message"), 2);
	TEST_ASSERT_EQUALS(get_message_type_id(0, "EnumMessage"), 3);
	TEST_ASSERT_EQUALS(get_message_type_id(0, "BoolMessage"), 4);

	TEST_ASSERT_EQUALS(get_message_type_id(3, "RequestTemperatureChange"), 0);
	TEST_ASSERT_EQUALS(get_message_type_id(3, "RefuseTemperatureChange"), 1);
	TEST_ASSERT_EQUALS(get_message_type_id(3, "AgreeToTemperatureChange"), 2);
	TEST_ASSERT_EQUALS(get_message_type_id(3, "TemperatureChangeEnacted"), 3);
	TEST_ASSERT_EQUALS(get_message_type_id(3, "TemperatureChangeFailed"), 4);

	TEST_ASSERT_EQUALS(get_message_type_id(7, "RequestProposal"), 0);
	TEST_ASSERT_EQUALS(get_message_type_id(7, "ProposeAction"), 1);
	TEST_ASSERT_EQUALS(get_message_type_id(7, "RefuseAction"), 2);
	TEST_ASSERT_EQUALS(get_message_type_id(7, "AcceptProposal"), 3);
	TEST_ASSERT_EQUALS(get_message_type_id(7, "RejectProposal"), 4);
}

void
CInterfaceTest::testMessageFromTypeId()
{
	int msg;

	msg = message_from_type_id(0, 0);
	TEST_ASSERT_TRUE(msg >= 0);
	TEST_ASSERT_EQUALS(message_get_size(msg), 1u);
}
