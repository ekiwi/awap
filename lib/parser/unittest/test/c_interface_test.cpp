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
CInterfaceTest::testX()
{
	TEST_ASSERT_EQUALS(1+1, 2);
}
