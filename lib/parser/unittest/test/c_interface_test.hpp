/**
 * c_interface_test.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <unittest/testsuite.hpp>

class CInterfaceTest : public unittest::TestSuite
{
public:
	void testGetTypeId();
	void testMessageFromTypeId();
	void testMessageAccess();
	void testBooleanFieldAccess();
	void testIntegerFieldAccess();
	void testEnumFieldAccess();
	void testUnmarshalPacket();
	void testMarshalPacket();
};
