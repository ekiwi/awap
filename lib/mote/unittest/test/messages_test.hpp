/**
 * messages_test.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <unittest/testsuite.hpp>

class MessagesTest : public unittest::TestSuite
{
public:
	void setUp();
	void testCommonHeaderParsing();
	void testSimpleUInt32Message();
	void testSimpleUInt12Message();
	void testBoolMessage();
	void testMessageFactory();
};
