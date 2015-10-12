/**
 * messages_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "messages_test.hpp"
#include <awap.hpp>
#include <debug.hpp>
#include <generated/messages.hpp>
#include <jlib_awap-common.hpp>
using namespace awap;
using namespace generated::MessageTestService;

void
MessagesTest::setUp()
{
	Awap::init(0x1234);
}

void
MessagesTest::testSimpleUInt32Message()
{
	// test service
	using JavaClass = SimpleUInt32Message::JavaClass;

	{
		// prepare SimpleUInt32Message body (leading two bytes are message header)
		uint8_t msg[7] = { 0x00, 0x00, 0x01, 0x23, 0x45, 0x67, 0x80 };

		// parse to Java Object
		RxSimpleUInt32Message rx(0, slice(msg));
		ref_t obj = rx.createJavaObject();
		TEST_ASSERT_FALSE(obj == 0);
		auto obj_struct = static_cast<JavaClass::UnderlyingType*>(REF_TO_VOIDP(obj));
		TEST_ASSERT_EQUALS(obj_struct->uint_value, 0x12345678);

		// test that 32bits were read
		uint8_t out[7] = { 0, 0, 0, 0, 0, 0, 0 };
		// 32bit payload + 4bit message id + 2 byte common header
		TxSimpleUInt32Message tx(0, slice(out));
		TEST_ASSERT_EQUALS(tx.loadFromJavaObject(obj), 7u);
		// message id is 1 and should be set by the `fromJava` method
		msg[2] |= (1 << 4);
		TEST_ASSERT_EQUALS_ARRAY(msg, out, slice(msg).length);
	}

	{
		// create Java message object
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->uint_value = 57343298;

		// to message...
		uint8_t msg[7];
		// 32bit payload + 4bit message id + 2 byte common header
		TxSimpleUInt32Message tx(0, slice(msg));
		TEST_ASSERT_EQUALS(tx.loadFromJavaObject(obj.getRef()), 7u);
		// ...and back
		RxSimpleUInt32Message rx(0, slice(msg));
		ref_t out = rx.createJavaObject();
		TEST_ASSERT_FALSE(out == 0);

		auto obj_struct = static_cast<JavaClass::UnderlyingType*>(REF_TO_VOIDP(out));
		TEST_ASSERT_EQUALS(obj_struct->uint_value, 57343298);
	}

}

void
MessagesTest::testSimpleUInt12Message()
{
	// test service
	using JavaClass = SimpleUInt12Message::JavaClass;

	{
		// prepare SimpleUInt12Message body
		uint8_t msg[4] = { 0x00, 0x00, 0x06, 0x078 };

		// parse to Java Object
		RxSimpleUInt12Message rx(0, slice(msg));
		ref_t obj = rx.createJavaObject();
		TEST_ASSERT_FALSE(obj == 0);

		uint8_t out[4] = { 0, 0, 0, 0 };
		// 12bit payload + 4bit message id + 2 byte common header
		TxSimpleUInt12Message tx(0, slice(out));
		TEST_ASSERT_EQUALS(tx.loadFromJavaObject(obj), 4u);
		// message id is 2 and should be set by the `fromJava` method
		msg[2] |= (2 << 4);
		TEST_ASSERT_EQUALS_ARRAY(msg, out, slice(msg).length);
	}

	{
		// create Java message object
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->uint_value = 1234;

		// to message...
		uint8_t msg[4];
		// 12bit payload + 4bit message id + 2 byte common header
		TxSimpleUInt12Message tx(0, slice(msg));
		TEST_ASSERT_EQUALS(tx.loadFromJavaObject(obj.getRef()), 4u);
		// ...and back
		RxSimpleUInt12Message rx(0, slice(msg));
		ref_t out = rx.createJavaObject();
		TEST_ASSERT_FALSE(out == 0);

		auto out_raw = static_cast<JavaClass::UnderlyingType*>(REF_TO_VOIDP(out));
		TEST_ASSERT_EQUALS(out_raw->uint_value, 1234);
	}

}

void
MessagesTest::testBoolMessage()
{
	// test service
	using JavaClass = BoolMessage::JavaClass;

	{
		// create Java message object
		JavaClass obj(debug::getAwapCommonInfusion());
		auto raw = obj.getUnderlying();
		raw->b0 = true;
		raw->b1 = false;
		raw->b2 = true;

		// to message...
		uint8_t msg[3];
		// 3 x 1bit bool + 4bit message id + 2 byte common header
		TxBoolMessage tx(0, slice(msg));
		TEST_ASSERT_EQUALS(tx.loadFromJavaObject(obj.getRef()), 3u);
		TEST_ASSERT_EQUALS(msg[2], (4 << 4) | (0b1010));
		// ...and back
		RxBoolMessage rx(0, slice(msg));
		ref_t out = rx.createJavaObject();
		TEST_ASSERT_FALSE(out == 0);

		auto out_raw = static_cast<JavaClass::UnderlyingType*>(REF_TO_VOIDP(out));
		TEST_ASSERT_EQUALS(out_raw->b0, true);
		TEST_ASSERT_EQUALS(out_raw->b1, false);
		TEST_ASSERT_EQUALS(out_raw->b2, true);
	}

}

void
MessagesTest::testMessageFactory()
{
/*
	auto getMessages = generated::MessagesFactory::getMessages;
	using Service = generated::MessagesFactory::MessageTestService;
	const uint8_t MessageTestServiceId = 0;

	// test with valid SimpleUInt32Message
	{
		uint8_t msg[5] = { 0x01 | (1 << 4), 0x23, 0x45, 0x67, 0x80 };
		auto parser = getMessages(MessageTestServiceId, slice(msg));
		TEST_ASSERT_EQUALS(parser.createJava, Service::createJava_SimpleUInt32Message);
	}

	// test with invalid message id
	{
		uint8_t msg[4] = { 0x01 | (0xf << 4), 0x23, 0x45, 0x67 };
		auto parser = getMessages(MessageTestServiceId, slice(msg));
		TEST_ASSERT_EQUALS(parser.createJava, static_cast<void*>(nullptr));
	}
	*/
}
