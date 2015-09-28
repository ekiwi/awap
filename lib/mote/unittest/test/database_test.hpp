/**
 * database_test.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <unittest/testsuite.hpp>

class DatabaseTest : public unittest::TestSuite
{
public:
	void testInsert();
	void testFind();
	void testRemove();
};
