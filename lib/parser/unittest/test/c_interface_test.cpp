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

#define TEST_GET_STRING(method, string)      \
{                                            \
	char str[20];                            \
	TEST_ASSERT_TRUE(method(msg, str, 20));  \
	TEST_ASSERT_EQUALS_STRING(str, string);  \
}

void
CInterfaceTest::testMessageAccess()
{
	auto msg = message_from_type_id(0, get_message_type_id(0, "BoolMessage"));
	TEST_ASSERT_TRUE(msg >= 0);

	// constant message type properties
	TEST_ASSERT_EQUALS(message_get_size(msg), 1u);
	TEST_ASSERT_EQUALS(message_get_type_id(msg), 4);
	TEST_ASSERT_EQUALS(message_get_service_type_id(msg), 0);
	TEST_GET_STRING(message_get_name, "BoolMessage");
	TEST_GET_STRING(message_get_service_name, "MessageTestService");
	TEST_GET_STRING(message_get_performative, "INFORM");
	TEST_ASSERT_FALSE(message_is_service_tx_message(msg));
	TEST_ASSERT_EQUALS(message_get_number_of_fields(msg), 3u);

	// data that can change in each individual message
	message_set_is_broadcast(msg, true);
	TEST_ASSERT_TRUE(message_is_broadcast(msg));
	message_set_is_broadcast(msg, false);
	TEST_ASSERT_FALSE(message_is_broadcast(msg));

	message_set_dest_agent_id(msg, 3);
	TEST_ASSERT_EQUALS(message_get_dest_agent_id(msg), 3);
	message_set_dest_agent_id(msg, 7);
	TEST_ASSERT_EQUALS(message_get_dest_agent_id(msg), 7);

	message_set_src_agent_id(msg, 0);
	TEST_ASSERT_EQUALS(message_get_src_agent_id(msg), 0);
	TEST_ASSERT_EQUALS(message_get_dest_agent_id(msg), 7);
	message_set_src_agent_id(msg, 4);
	TEST_ASSERT_EQUALS(message_get_src_agent_id(msg), 4);
}

void
CInterfaceTest::testBooleanFieldAccess()
{
	auto msg = message_from_type_id(0, get_message_type_id(0, "BoolMessage"));
	TEST_ASSERT_TRUE(msg >= 0);

	auto b0 = message_get_field_id(msg, "b0");
	auto b1 = message_get_field_id(msg, "b1");
	auto b2 = message_get_field_id(msg, "b2");

	TEST_ASSERT_TRUE(message_set_boolean_field_value(msg, b0, true));
	TEST_ASSERT_EQUALS(message_get_boolean_field_value(msg, b0), true);
	TEST_ASSERT_TRUE(message_set_boolean_field_value(msg, b0, false));
	TEST_ASSERT_EQUALS(message_get_boolean_field_value(msg, b0), false);

	TEST_ASSERT_TRUE(message_set_boolean_field_value(msg, b0, true));
	TEST_ASSERT_TRUE(message_set_boolean_field_value(msg, b1, true));
	TEST_ASSERT_TRUE(message_set_boolean_field_value(msg, b2, true));
	TEST_ASSERT_EQUALS(message_get_boolean_field_value(msg, b0), true);
	TEST_ASSERT_EQUALS(message_get_boolean_field_value(msg, b1), true);
	TEST_ASSERT_EQUALS(message_get_boolean_field_value(msg, b2), true);

	release_message(msg);
}

void
CInterfaceTest::testIntegerFieldAccess()
{
	auto msg = message_from_type_id(0, 2);	// SimpleUInt12Message
	TEST_ASSERT_TRUE(msg >= 0);

	auto value_id = message_get_field_id(msg, "uint_value");
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 4));
	TEST_ASSERT_EQUALS(message_get_integer_field_value(msg, value_id), 4);

	// the range of a 12bit unsigned integer is 0 - 4095
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 0));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, -1));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, -2000));
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 4095));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, 4096));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, 1000000));

	release_message(msg);
}

void
CInterfaceTest::testEnumFieldAccess()
{
	auto msg = message_from_type_id(0, get_message_type_id(0, "EnumMessage"));
	TEST_ASSERT_TRUE(msg >= 0);

	auto value_id = message_get_field_id(msg, "enum_value");
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 1));
	TEST_ASSERT_EQUALS(message_get_integer_field_value(msg, value_id), 1);
	char str[20];
	TEST_ASSERT_TRUE(message_get_enum_field_string_value(msg, value_id, str, 20));
	TEST_ASSERT_EQUALS_STRING(str, "HK1Toaster");

	// Building can contain a maximum of 16 different values
	// but only Build1(0), HK1Toaster(1) and SemiTemp(2) are defined
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 0));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, -1));
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 15));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, 16));
	TEST_ASSERT_FALSE(message_set_integer_field_value(msg, value_id, 200));
	TEST_ASSERT_TRUE(message_set_enum_field_string_value(msg, value_id, "Build1"));
	TEST_ASSERT_TRUE(message_set_enum_field_string_value(msg, value_id, "HK1Toaster"));
	TEST_ASSERT_TRUE(message_set_enum_field_string_value(msg, value_id, "SemiTemp"));
	TEST_ASSERT_FALSE(message_set_enum_field_string_value(msg, value_id, "OtherRoom"));

	release_message(msg);
}

void
CInterfaceTest::testUnmarshalPacket()
{
	// prepare SimpleUInt32Message body (leading two bytes are message header)
	uint8_t msg_data[7] = { 0x00, 0x00, (1<<4) | 0x01, 0x23, 0x45, 0x67, 0x80 };

	auto msg = message_unmarshal(msg_data, 7);
	TEST_ASSERT_TRUE(msg >= 0);
	TEST_GET_STRING(message_get_name, "SimpleUInt32Message");

	auto value_id = message_get_field_id(msg, "uint_value");
	TEST_ASSERT_EQUALS(message_get_integer_field_value(msg, value_id), 0x12345678);

	release_message(msg);
}

void
CInterfaceTest::testMarshalPacket()
{
	auto msg = message_from_type_id(0, get_message_type_id(0, "SimpleUInt32Message"));
	TEST_ASSERT_TRUE(msg >= 0);

	auto value_id = message_get_field_id(msg, "uint_value");
	TEST_ASSERT_TRUE(message_set_integer_field_value(msg, value_id, 0x12345678));

	uint8_t msg_data[7] = { 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
	TEST_ASSERT_TRUE(message_marshal(msg, msg_data, 7));
	const uint8_t expected_msg_data[7] = { 0x00, 0x00, (1<<4) | 0x01, 0x23, 0x45, 0x67, 0x80 };
	TEST_ASSERT_EQUALS_ARRAY(msg_data, expected_msg_data, 7);

	release_message(msg);
}
