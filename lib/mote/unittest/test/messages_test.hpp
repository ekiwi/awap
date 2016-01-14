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
	void setUp() override;
	void tearDown() override;
	void testCommonHeaderParsing();
	void testSimpleIntMessage();
	void testSimpleShortMessage();
	void testBoolMessage();
	void testMakeRxMessage();
	void testMakeTxMessage();
};
