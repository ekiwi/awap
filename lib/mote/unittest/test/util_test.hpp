/**
 * util_test.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <unittest/testsuite.hpp>

class UtilTest : public unittest::TestSuite
{
public:
	void testArrayCount();
	void testDivideCeil();
	void testString();
};
