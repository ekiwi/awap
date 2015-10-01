/**
 * bitread_test.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "bitread_test.hpp"


struct NibbleSwap {
	uint8_t a : 4;
	uint8_t b : 4;
} __attribute__((packed));

struct Offset4UInt {
	uint8_t : 4;
	uint32_t value : 32;
	uint8_t : 4;
}__attribute__((packed));

struct Offset8UInt {
	uint8_t : 8;
	uint32_t value : 32;
	uint8_t : 0;
}__attribute__((packed));

void
BitreadTest::testBitfields()
{
	const uint8_t inpByte = 0x9A;
	auto nibble = reinterpret_cast<const NibbleSwap*>(&inpByte);
	TEST_ASSERT_EQUALS(nibble->a, 0xA);
	TEST_ASSERT_EQUALS(nibble->b, 0x9);

	const uint32_t inp32 = 0x12345678;
	const uint8_t outBytes[4] = { 0x78, 0x56, 0x34, 0x12 };
	auto inpBytes = reinterpret_cast<const uint8_t*>(&inp32);
	TEST_ASSERT_EQUALS_ARRAY(inpBytes, outBytes, 4u);

	const uint8_t inpOffset4Bytes[5] = { 0x80, 0x67, 0x45, 0x23, 0x01 };
	const uint8_t inpOffset8Bytes[5] = { 0x00, 0x78, 0x56, 0x34, 0x12};
	auto offset4 = reinterpret_cast<const Offset4UInt*>(&inpOffset4Bytes)->value;
	auto offset8 = reinterpret_cast<const Offset8UInt*>(&inpOffset8Bytes)->value;
	TEST_ASSERT_EQUALS(offset4, 0x12345678u);
	TEST_ASSERT_EQUALS(offset8, 0x12345678u);
}
