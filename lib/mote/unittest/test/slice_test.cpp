/**
 * slice_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "slice_test.hpp"

#include <util.hpp>
using namespace awap;


void
SliceTest::testSlice()
{
	char sliceDataA[20] = { 0 };
	auto sliceA = slice(sliceDataA);
	TEST_ASSERT_EQUALS(sliceA.data, sliceDataA);
	TEST_ASSERT_EQUALS(sliceA.length, 20u);

	// test if increment
	for(auto ii = 0; ii < 20; ++ii) {
		TEST_ASSERT_FALSE(sliceA.isEmpty());
		sliceA.increment();
	}
	TEST_ASSERT_TRUE(sliceA.isEmpty());
	// reset sliceA
	sliceA = slice(sliceDataA);

	char sliceDataB[15] = { 0 };
	auto sliceB = slice(sliceDataB);
	TEST_ASSERT_EQUALS(sliceB.data, sliceDataB);
	TEST_ASSERT_EQUALS(sliceB.length, 15u);

	// compare slices of different lengths
	TEST_ASSERT_FALSE(sliceA == sliceB);
	// compare slices of equal length and same content (zeros)
	TEST_ASSERT_TRUE(sliceA.sub(0,15) == sliceB);
	TEST_ASSERT_TRUE(sliceA.sub(4,19) == sliceB);

	// test write
	const char testStr[12] = "Hello World";
	sliceA.write(testStr);
	TEST_ASSERT_EQUALS_STRING(sliceDataA, "Hello World");
	TEST_ASSERT_EQUALS(sliceA.data, sliceDataA + 12);
	TEST_ASSERT_EQUALS(sliceA.length, 20u - 12u);

	// make sure write does not leave slice
	{
		char data[10] = { 0 };
		slice(data).sub(0,3).write(testStr);

		// TODO: currently write just doesn't do anything when the
		//       slice is not big enough
		//       What should be the expected behavior?
		char expected[10] = { 'H', 'e', 'l', 0, 0, 0, 0, 0, 0, 0 };
		TEST_ASSERT_EQUALS_ARRAY(data, expected, 10);
	}
}

void
SliceTest::testSubSlice()
{
	uint8_t data[5] = { 0, 1, 2, 3, 4 };
	auto sl = slice(data);

	// start = 0, end > 0
	TEST_ASSERT_TRUE(sl.sub() == sl);
	TEST_ASSERT_TRUE(sl.sub(0,2) == Slice<uint8_t>(data, 2));
	TEST_ASSERT_TRUE(sl.sub(0,5) == sl);

	// start = 0, end < 0
	TEST_ASSERT_TRUE(sl.sub(0,-2) == Slice<uint8_t>(data, 3));
	TEST_ASSERT_TRUE(sl.sub(0,-1) == Slice<uint8_t>(data, 4));
	TEST_ASSERT_TRUE(sl.sub(0,-4) == Slice<uint8_t>(data, 1));
	TEST_ASSERT_TRUE(sl.sub(0,-5).isEmpty());

	// end > 0, start > 0
	TEST_ASSERT_TRUE(sl.sub(1,5) == Slice<uint8_t>(data+1, 4));
	TEST_ASSERT_TRUE(sl.sub(4,5) == Slice<uint8_t>(data+4, 1));
	TEST_ASSERT_TRUE(sl.sub(2,3) == Slice<uint8_t>(data+2, 1));

	// end < 0, start < 0
	TEST_ASSERT_TRUE(sl.sub(-2,-1) == Slice<uint8_t>(data+3, 1));
	TEST_ASSERT_TRUE(sl.sub(-4,-1) == Slice<uint8_t>(data+1, 3));
	TEST_ASSERT_TRUE(sl.sub(-2)    == Slice<uint8_t>(data+3, 2));

	// start, end, invalid values
	TEST_ASSERT_TRUE(sl.sub(0,10) == sl);
	TEST_ASSERT_TRUE(sl.sub(0,-10).isEmpty());
	TEST_ASSERT_TRUE(sl.sub(3,2).isEmpty());
	TEST_ASSERT_TRUE(sl.sub(-2,-3).isEmpty());
}
