#include "slice_test.hpp"

#include <util.hpp>
using namespace awap;


void
SliceTest::testSlice()
{
	uint8_t sliceDataA[20];
	auto sliceA = slice(sliceDataA);
	TEST_ASSERT_EQUALS(sliceA.data, sliceDataA);
	TEST_ASSERT_EQUALS(sliceA.length, 20);

	// test if increment
	for(auto ii = 0; ii < 20; ++ii) {
		TEST_ASSERT_FALSE(sliceA.isEmpty());
		sliceA.increment();
	}
	TEST_ASSERT_TRUE(sliceA.isEmpty());
	// reset sliceA
	sliceA = slice(sliceDataA);

	uint8_t sliceDataB[15];
	auto sliceB = slice(sliceDataB);
	TEST_ASSERT_EQUALS(sliceB.data, sliceDataB);
	TEST_ASSERT_EQUALS(sliceB.length, 15);

	// compare slices of different lengths
	TEST_ASSERT_FALSE(sliceA == sliceB);

	
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
	TEST_ASSERT_TRUE(sl.sub(0,10) == sl);

	// start = 0, end < 0
	TEST_ASSERT_TRUE(sl.sub(0,-2) == Slice<uint8_t>(data, 3));
	TEST_ASSERT_TRUE(sl.sub(0,-1) == Slice<uint8_t>(data, 4));
	TEST_ASSERT_TRUE(sl.sub(0,-4) == Slice<uint8_t>(data, 1));
	TEST_ASSERT_TRUE(sl.sub(0,-5).isEmpty());
	TEST_ASSERT_TRUE(sl.sub(0,-10).isEmpty());

	// end > 0, start > 0
	TEST_ASSERT_TRUE(sl.sub(1,5) == Slice<uint8_t>(data+1, 4));
	TEST_ASSERT_TRUE(sl.sub(4,5) == Slice<uint8_t>(data+4, 1));
	TEST_ASSERT_TRUE(sl.sub(2,3) == Slice<uint8_t>(data+2, 1));
}
