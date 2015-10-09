/**
 * message_parser_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "message_parser_test.hpp"
#include <awap.hpp>
#include <debug.hpp>
#include <generated/message_parser.hpp>
#include <jlib_awap-common.hpp>
using namespace awap;

void
MessageParserTest::setUp()
{
	Awap::init(0x1234);
}

void
MessageParserTest::testSimpleUInt32Message()
{
	// test service
	using Service = generated::MessageParserFactory::MessageTestService;

	{
		// prepare SimpleUInt32Message body
		uint8_t msg[5] = { 0x01, 0x23, 0x45, 0x67, 0x80 };

		// parse to Java Object
		ref_t obj = Service::createJava_SimpleUInt32Message(slice(msg));
		TEST_ASSERT_FALSE(obj == 0);
		auto obj_uint_raw = *static_cast<uint32_t*>(REF_TO_VOIDP(obj));
		TEST_ASSERT_EQUALS(obj_uint_raw, 0x12345678u);

		// test that 32bits were read
		uint8_t out[5] = { 0, 0, 0, 0, 0 };
		// 32bit payload + 4bit message id
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt32Message(obj, slice(out)), 5u);
		// message id is 1 and should be set by the `fromJava` method
		msg[0] |= (1 << 4);
		TEST_ASSERT_EQUALS_ARRAY(msg, out, slice(msg).length);
	}

	{
		// create Java message object
		using JavaClass = ::de::rwth_aachen::awap::messages::MessageTestService::SimpleUInt32Message;
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->uint_value = -57343298;

		// to message...
		uint8_t msg[5];
		// 32bit payload + 4bit message id
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt32Message(obj.getRef(), slice(msg)), 5u);
		// ...and back
		ref_t out = Service::createJava_SimpleUInt32Message(slice(msg));
		TEST_ASSERT_FALSE(out == 0);

		auto out_raw = *static_cast<int32_t*>(REF_TO_VOIDP(out));;
		TEST_ASSERT_EQUALS(out_raw, -57343298);
	}

}

void
MessageParserTest::testSimpleUInt12Message()
{
	// test service
	using Service = generated::MessageParserFactory::MessageTestService;

	{
		// prepare SimpleUInt12Message body
		uint8_t msg[2] = { 0x06, 0x078 };

		// parse to Java Object
		ref_t obj = Service::createJava_SimpleUInt12Message(slice(msg));
		TEST_ASSERT_FALSE(obj == 0);

		uint8_t out[2] = { 0, 0 };
		// 12bit payload + 4bit message id
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt12Message(obj, slice(out)), 2u);
		// message id is 2 and should be set by the `fromJava` method
		msg[0] |= (2 << 4);
		TEST_ASSERT_EQUALS_ARRAY(msg, out, slice(msg).length);
	}

	{
		// create Java message object
		using JavaClass = ::de::rwth_aachen::awap::messages::MessageTestService::SimpleUInt12Message;
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->uint_value = -1234;

		// to message...
		uint8_t msg[2];
		// 12bit payload + 4bit message id
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt12Message(obj.getRef(), slice(msg)), 2u);
		// ...and back
		ref_t out = Service::createJava_SimpleUInt12Message(slice(msg));
		TEST_ASSERT_FALSE(out == 0);

		auto out_raw = *static_cast<int16_t*>(REF_TO_VOIDP(out));
		TEST_ASSERT_EQUALS(out_raw, -1234);
	}

}

void
MessageParserTest::testMessageParserFactory()
{
	auto getMessageParser = generated::MessageParserFactory::getMessageParser;
	using Service = generated::MessageParserFactory::MessageTestService;
	const uint8_t MessageTestServiceId = 0;

	// test with valid SimpleUInt32Message
	{
		uint8_t msg[5] = { 0x01, 0x23, 0x45, 0x67, 0x80 };
		auto parser = getMessageParser(MessageTestServiceId, slice(msg));
		TEST_ASSERT_EQUALS(parser.createJava, Service::createJava_SimpleUInt32Message);
	}

	// test with invalid SimpleUInt32Message
	{
		uint8_t msg[4] = { 0x01, 0x23, 0x45, 0x67 };
		auto parser = getMessageParser(MessageTestServiceId, slice(msg));
		TEST_ASSERT_EQUALS(parser.createJava, static_cast<void*>(nullptr));
	}
}
