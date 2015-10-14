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
	void testToQueryMask();
	void testToBroadcastHeader();
	void testToQueryMaskWithServiceIdAndBroadcastHeader();
	void testGetServiceTypeId();
};