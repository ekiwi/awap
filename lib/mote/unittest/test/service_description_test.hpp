/**
 * service_description_test.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <unittest/testsuite.hpp>

class ServiceDescriptionTest : public unittest::TestSuite
{
public:
	void setUp() override;
	void testToBroadcastHeader();
	void testGetServiceTypeId();
	void testGetPropertySize();
	void testToQueryMaskWithServiceIdAndBroadcastHeader();
	void testToQueryMask();
	void testMarshalServiceDescription();
};
