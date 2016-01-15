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
	Awap::init();
}

void
ServiceDescriptionTest::tearDown()
{
	Awap::deinit();
}

void
ServiceDescriptionTest::testToBroadcastHeader()
{
	using SD = awap::generated::ServiceDescription;

	EnergySupplyServiceDescription obj(getAwapCommonInfusion(), 0);
	auto data = obj.getUnderlying();
	TEST_ASSERT_EQUALS(SD::toBroadcastHeader(obj.getRef()), 0b00000000);

	data->buildingDoNotCare = 0;
	TEST_ASSERT_EQUALS(SD::toBroadcastHeader(obj.getRef()), 0b10000000);

	data->buildingDoNotCare = 1;
	data->supplyCircuitDoNotCare = 0;
	TEST_ASSERT_EQUALS(SD::toBroadcastHeader(obj.getRef()), 0b01000000);

	data->buildingDoNotCare = 0;
	data->supplyCircuitDoNotCare = 0;
	data->roomDoNotCare = 0;
	TEST_ASSERT_EQUALS(SD::toBroadcastHeader(obj.getRef()), 0b11100000);

}

void
ServiceDescriptionTest::testGetServiceTypeId()
{
	using SD = awap::generated::ServiceDescription;

	MessageTestServiceDescription testDesc(getAwapCommonInfusion(), 0);
	TEST_ASSERT_EQUALS(SD::getServiceTypeId(testDesc.getRef()), 0);

	EnergySupplyServiceDescription energySupplyDesc(getAwapCommonInfusion(), 0);
	TEST_ASSERT_EQUALS(SD::getServiceTypeId(energySupplyDesc.getRef()), 7);

	RoomServiceDescription roomDesc(getAwapCommonInfusion(), 0);
	TEST_ASSERT_EQUALS(SD::getServiceTypeId(roomDesc.getRef()), 3);
}

void
ServiceDescriptionTest::testGetPropertySize()
{
	using SD = awap::generated::ServiceDescription;

	// MessageTestService: id: 0
	TEST_ASSERT_EQUALS(SD::getPropertySize(0), 0);

	// EnergySupplyService: id: 7
	TEST_ASSERT_EQUALS(SD::getPropertySize(7), 3);

	// RoomService: id: 3
	TEST_ASSERT_EQUALS(SD::getPropertySize(3), 3);
}

void
ServiceDescriptionTest::testToQueryMaskWithServiceIdAndBroadcastHeader()
{
	using SD = awap::generated::ServiceDescription;

	uint32_t out[1];
	auto out_bytes = reinterpret_cast<const uint8_t*>(out);

	{
		out[0] = 0xaaaaaaaau;
		TEST_ASSERT_TRUE(SD::toQueryMask(0, 0b00000000, slice(out)));
		// mask should be all zero, because the TestMessageService does not
		// contain any properties
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);
	}

	{
		// EnergySupplyService: id: 7
		out[0] = 0xaaaaaaaau;
		TEST_ASSERT_TRUE(SD::toQueryMask(7, 0b00000000, slice(out)));
		// no properties selected
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);

		out[0] = 0xaaaaaaaau;
		TEST_ASSERT_TRUE(SD::toQueryMask(7, 0b10000000, slice(out)));
		// Building property (8bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[1], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);

		out[0] = 0xaaaaaaaau;
		TEST_ASSERT_TRUE(SD::toQueryMask(7, 0b01000000, slice(out)));
		// SupplyCircuit property (8bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);

		out[0] = 0xaaaaaaaau;
		TEST_ASSERT_TRUE(SD::toQueryMask(7, 0b11100000, slice(out)));
		// all properties selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[2], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);
	}
}

void
ServiceDescriptionTest::testToQueryMask()
{
	using SD = awap::generated::ServiceDescription;

	// currently the largest service description needs 20 bit
	// this will be rounded up to 32bit => 4 byte
	uint32_t out[1];
	// while the service directory works with 32bit integer values
	// we use 8bit integers to generate the mask and service descriptions
	// this makes the position of the mask bytes in the uint32_t
	// depended on endianness
	// this does not matter for our application, as it all stays on the
	// same platform
	// however, it makes it harder to test, thus we use byte access
	// for this
	auto out_bytes = reinterpret_cast<const uint8_t*>(out);

	{
		out[0] = 0xaaaaaaaau;
		// test with TestMessageService which does not have any properties
		MessageTestServiceDescription obj(getAwapCommonInfusion(), 0);
		TEST_ASSERT_TRUE(SD::toQueryMask(obj.getRef(), slice(out)));
		// mask should be all zero, because the TestMessageService does not
		// contain any properties
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);
	}

	{
		out[0] = 0xaaaaaaaau;
		EnergySupplyServiceDescription obj(getAwapCommonInfusion(), 0);
		auto data = obj.getUnderlying();
		TEST_ASSERT_TRUE(SD::toQueryMask(
			obj.getRef(), slice(out)));
		// no properties selected
		TEST_ASSERT_EQUALS(out[0], 0x00000000u);

		out[0] = 0xaaaaaaaau;
		data->buildingDoNotCare = 0;
		TEST_ASSERT_TRUE(SD::toQueryMask(obj.getRef(), slice(out)));
		// Building property (8bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[1], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);

		out[0] = 0xaaaaaaaau;
		data->buildingDoNotCare = 1;
		data->supplyCircuitDoNotCare = 0;
		TEST_ASSERT_TRUE(SD::toQueryMask(obj.getRef(), slice(out)));
		// SupplyCircuit property (8bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);

		out[0] = 0xaaaaaaaau;
		data->buildingDoNotCare = 0;
		data->supplyCircuitDoNotCare = 0;
		data->roomDoNotCare = 0;
		TEST_ASSERT_TRUE(SD::toQueryMask(obj.getRef(), slice(out)));
		// all properties selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[2], 0xffu);
		TEST_ASSERT_EQUALS(out_bytes[3], 0x00u);
	}
}

void
ServiceDescriptionTest::testMarshalServiceDescription()
{
	using SD = awap::generated::ServiceDescription;

	uint32_t out[1];
	auto out_bytes = reinterpret_cast<uint8_t*>(out);

	{
		// test with TestMessageService which does not have any properties
		MessageTestServiceDescription obj(getAwapCommonInfusion(), 0);
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out)), 0u);
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out_bytes, 4)), 0u);
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out_bytes, 0)), 0u);
	}

	{
		out[0] = 0;
		EnergySupplyServiceDescription obj(getAwapCommonInfusion(), 0);
		auto data = obj.getUnderlying();
		data->building = 0xf;
		// marshal always writes the maximum number of bytes needed for the service
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out)), 3u);
		TEST_ASSERT_EQUALS(out_bytes[0], 0x0f);
		TEST_ASSERT_EQUALS(out_bytes[1], 0x00);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00);


		out[0] = 0xaaaaaaaau;
		data->building = 0;
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out)), 3u);
		// Building property (4bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0x00);
		TEST_ASSERT_EQUALS(out_bytes[1], 0x00);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00);

		out[0] = 0;
		data->supplyCircuit = 0xaa;
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out)), 3u);
		// SupplyCircuit property (8bit) selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0x00u);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xaau);
		TEST_ASSERT_EQUALS(out_bytes[2], 0x00u);

		out[0] = 0x11111111u;
		data->building = 0xa;
		data->supplyCircuit = 0xbb;
		data->room = 0xcc;
		TEST_ASSERT_EQUALS(SD::marshal(obj.getRef(), slice(out)), 3u);
		// all properties selected
		TEST_ASSERT_EQUALS(out_bytes[0], 0x0au);
		TEST_ASSERT_EQUALS(out_bytes[1], 0xbbu);
		TEST_ASSERT_EQUALS(out_bytes[2], 0xccu);
	}
}
