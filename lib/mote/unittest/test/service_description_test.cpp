/**
 * service_description_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "service_description_test.hpp"
#include <common.hpp>
#include <generated/service_descriptions.hpp>
#include <jlib_awap-common.hpp>
using namespace awap;

void
ServiceDescriptionTest::setUp()
{
	Awap::init(0x4321);
}


void
ServiceDescriptionTest::testMessageTestService()
{
	using ServiceDescription = ::de::rwth_aachen::awap::service::MessageTestServiceDescription;

	// currently the largest service description needs 20 bit
	// this will be rounded up to 32bit => 4 byte
	uint8_t out[4] = { 0xaa, 0xaa, 0xaa, 0xaa };

	ServiceDescription obj(getAwapCommonInfusion(), 0);
	TEST_ASSERT_TRUE(awap::generated::ServiceDescription::toMask(obj.getRef(), slice(out)));
	// mask should be all zero, because the TestMessageService does not contain any properties
	TEST_ASSERT_EQUALS(out[0], 0x00);
	TEST_ASSERT_EQUALS(out[1], 0x00);
	TEST_ASSERT_EQUALS(out[2], 0x00);
	TEST_ASSERT_EQUALS(out[3], 0x00);
}
