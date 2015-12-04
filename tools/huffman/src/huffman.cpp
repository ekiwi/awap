/**
 * huffman.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include "huffman.hpp"

using namespace awap;

namespace huffman {

/// contains up to 32bit that will be right aligned
struct CodeBits
{
	uint32_t bits;
	uint32_t count;	// number of bits that are valid
};

class SymbolSource
{
	Slice<const uint8_t> source;
	CodeBits codeBits = { 0, 0 };

public:
	SymbolSource(const Slice<const uint8_t> src) :
		source(src),
		codeBits() {
		updateCodeBits(0);
	}

	const CodeBits& getCodeBits() const {
		return codeBits;
	}

	size_t getRemainingBits() const {
		return source.length * 8 + codeBits.count;
	}

	size_t updateCodeBits(uint32_t usedBits) {
		// discard used bits
		codeBits.bits <<= usedBits;
		codeBits.count -= usedBits;

		// refill code bits
		while(codeBits.count <= (32 - 8) && source.length > 0) {
			uint32_t byte = source.data[0];
			source.increment();
			codeBits.bits |= byte << (32 - codeBits.count - 8);
			codeBits.count += 8;
		}

		return source.length;
	}
};

template<uint32_t Code, uint32_t Bits>
struct Symbol
{
	static constexpr uint32_t ZeroBits = 32 - Bits;
	static constexpr uint32_t Mask = ((1 << Bits) - 1) << ZeroBits;
	static constexpr uint32_t Compare = Code << ZeroBits;
	/// returns how many bits where matched
	static inline constexpr uint32_t match(const CodeBits input) {
		// check if enough valid bits to match this symbol
		if(input.count >= Bits) {
			if((input.bits & Mask) == Compare) {
				return Bits;
			}
		}
		return 0;
	}
};

#include <generated/code.hpp>

bool decode(const Slice<const uint8_t>& input, Slice<uint8_t>& output) {
	SymbolSource source(input);
	Slice<uint8_t> buffer = output;

	uint32_t bitsMatched = 0;
	while((bitsMatched = Code::decode_symbol(source.getCodeBits(), buffer))) {
		source.updateCodeBits(bitsMatched);
	}

	output.length = buffer.data - output.data;

	if(source.getRemainingBits() == 0) {
		return true;
	}

	if((source.getRemainingBits() / 8) == 0 && source.getCodeBits().bits == 0) {
		// assume trailing zeros
		return true;
	}

	return false;
}

} // namespace huffman
