/**
 * bit_slice_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "bit_slice_test.hpp"

#include <util.hpp>
using namespace awap;


void
BitSliceTest::testSizeMethods()
{
	uint8_t testBytes[4] = { 0b11011010, 0b10011001, 0x8a, 0xe4 };
	auto sl = bit_slice(testBytes);

	// test size and isEmtpy
	TEST_ASSERT_EQUALS(sl.bitCount(), arrayCount(testBytes) * 8u);
	TEST_ASSERT_EQUALS(sl.byteCount(), arrayCount(testBytes));
	TEST_ASSERT_FALSE(sl.isEmpty());
}


void
BitSliceTest::testStaticBitRead()
{
	uint8_t testBytes[8] = { 0b11011010, 0b10011001, 0x8a, 0xe4, 0x54, 0x56, 0x76, 0xab};
	auto sl = bit_slice(testBytes);

	// test readBits and count
	TEST_ASSERT_EQUALS(sl.readBits<3>(), 0b110);
	TEST_ASSERT_EQUALS(sl.bitCount(), (arrayCount(testBytes) * 8u) - 3);
	// byte count is always rounded down
	TEST_ASSERT_EQUALS(sl.byteCount(), arrayCount(testBytes) - 1u);
	TEST_ASSERT_EQUALS(sl.readBits<2>(), 3u);
	// read over byte boundary
	TEST_ASSERT_EQUALS(sl.readBits<7>(), 0b0101001);
	TEST_ASSERT_EQUALS(sl.bitCount(), (arrayCount(testBytes) * 8u) - 12);
	TEST_ASSERT_EQUALS(sl.byteCount(), arrayCount(testBytes) - 2u);
	// read value bigger than one byte (0b1001 => 0x9)
	TEST_ASSERT_EQUALS(sl.readBits<12>(), 0x98a);
	TEST_ASSERT_EQUALS(sl.readBits<4>(), 0xe);
	// read biggest possible value (32bit)
	TEST_ASSERT_EQUALS(sl.readBits<32>(), 0x4545676a);
	TEST_ASSERT_EQUALS(sl.bitCount(), 4u);	// only 0xa left
	// try to read more than are available, this should currently
	// return 0
	// TODO: is there a better way to fail?
	TEST_ASSERT_EQUALS(sl.readBits<8>(), 0);
	// a failed read should not change the internal state
	TEST_ASSERT_EQUALS(sl.bitCount(), 4u);
	TEST_ASSERT_EQUALS(sl.readBits<4>(), 0xa);
	// should be empty now
	TEST_ASSERT_EQUALS(sl.bitCount(), 0u);
	TEST_ASSERT_EQUALS(sl.byteCount(), 0u);
	TEST_ASSERT_TRUE(sl.isEmpty());
}

void
BitSliceTest::testDynamicBitRead()
{
	// TODO
}

void
BitSliceTest::testStaticBitWrite()
{
	uint8_t testBytes[8] = { 0xaa };
	auto sl = bit_slice(testBytes);

	// TODO
}

void
BitSliceTest::testDynamicBitWrite()
{
	// TODO
}
