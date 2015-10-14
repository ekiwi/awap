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
using namespace de::rwth_aachen::awap::service;

void
ServiceDescriptionTest::setUp()
{
	Awap::init(0x4321);
}


void
ServiceDescriptionTest::testToMask()
{
	// currently the largest service description needs 20 bit
	// this will be rounded up to 32bit => 4 byte
	uint32_t out[1];

	{
		out[0] = 0xaaaaaaaau;
		// test with TestMessageService which does not have any properties
		MessageTestServiceDescription obj(getAwapCommonInfusion(), 0);
		TEST_ASSERT_TRUE(awap::generated::ServiceDescription::toMask(obj.getRef(), slice(out)));
		// mask should be all zero, because the TestMessageService does not
		// contain any properties
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);
	}

	{
		out[0] = 0xaaaaaaaau;
		EnergySupplyServiceDescription obj(getAwapCommonInfusion(), 0);
		auto data = obj.getUnderlying();
		TEST_ASSERT_TRUE(awap::generated::ServiceDescription::toMask(obj.getRef(), slice(out)));
		// no properties selected
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);

		out[0] = 0xaaaaaaaau;
		data->buildingDoNotCare = 0;
		TEST_ASSERT_TRUE(awap::generated::ServiceDescription::toMask(obj.getRef(), slice(out)));
		// Building property (4bit) selected
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);
	}
}
