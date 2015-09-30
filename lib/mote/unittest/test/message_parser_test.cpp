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
		uint8_t msg[4] = { 0x78, 0x56, 0x34, 0x12 };

		// parse to Java Object
		ref_t obj = Service::createJava_SimpleUInt32Message(slice(msg));
		TEST_ASSERT_FALSE(obj == 0);

		// test that 32bits were read
		uint8_t out[4];
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt32Message(obj, slice(out)), 32u);
		TEST_ASSERT_EQUALS_ARRAY(msg, out, slice(msg).length);
	}

	{
		// create Java message object
		using JavaClass = ::de::rwth_aachen::awap::messages::MessageTestService::SimpleUInt32Message;
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->uint_value = -57343298;

		// to message...
		uint8_t msg[4];
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt32Message(obj.getRef(), slice(msg)), 32u);
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
		uint8_t msg[2] = { 0x78, 0x06 };

		// parse to Java Object
		ref_t obj = Service::createJava_SimpleUInt12Message(slice(msg));
		TEST_ASSERT_FALSE(obj == 0);

		uint8_t out[2] = { 0, 0 };
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt12Message(obj, slice(out)), 12u);
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
		TEST_ASSERT_EQUALS(Service::fromJava_SimpleUInt12Message(obj.getRef(), slice(msg)), 12u);
		// ...and back
		ref_t out = Service::createJava_SimpleUInt12Message(slice(msg));
		TEST_ASSERT_FALSE(out == 0);

		auto out_raw = *static_cast<int16_t*>(REF_TO_VOIDP(out));;
		TEST_ASSERT_EQUALS(out_raw, -1234);
	}

}
