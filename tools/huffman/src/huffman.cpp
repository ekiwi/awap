#include <iostream>
#include <fstream>
#include <bitset>

#pragma GCC diagnostic ignored "-Wunused-variable"

template<typename T>
struct Slice
{
	Slice(T* ptr, size_t len) : data(ptr), length(len) {}

	T* data;
	size_t length;

	inline void increment() {
		++data;
		--length;
	}
};

template<typename T, size_t N>
inline Slice<T>& slice(T(&ptr)[N])
{
	Slice<T> sl(ptr, N);
	return sl;
}

/// contains up to 32bit that will be right aligned
struct CodeBits
{
	uint32_t bits;
	uint32_t count;	// number of bits that are valid
};

class SymbolSource
{
	Slice<uint8_t> source;
	CodeBits codeBits = { 0, 0 };

public:
	SymbolSource(Slice<uint8_t>& src) :
		source(src),
		codeBits() {
		updateCodeBits(0);
	}

	const CodeBits& getCodeBits() {
		return codeBits;
	}

	const size_t getRemainingBits() {
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

#include "code.hpp"

inline static bool decode(Slice<uint8_t> input, Slice<uint8_t> output) {
	SymbolSource source(input);

	uint32_t bitsMatched = 0;
	while(bitsMatched = Code::decode_symbol(source.getCodeBits())) {
		source.updateCodeBits(bitsMatched);
	}

	if(source.getRemainingBits() == 0) {
		return true;
	}

	if((source.getRemainingBits() / 8) == 0 && source.getCodeBits().bits == 0) {
		// assume trailing zeros
		return true;
	}

	return false;
}



int main(int argc, char* argv[]) {
	if(argc < 2) {
		std::cout << argv[0] << " COMPRESSED [ORIGINAL]" << std::endl;
		return 1;
	}
	std::string compressed(argv[1]);

	std::ifstream input(compressed, std::ios::in|std::ios::binary|std::ios::ate);
	if(!input.is_open()) {
		std::cout << "could not open " << compressed << std::endl;
		return 2;
	}


	size_t size = input.tellg();
	char content[size];
	input.seekg (0, std::ios::beg);
	input.read (content, size);
	input.close();

	std::cout << "Trying to decompress input: " << compressed << std::endl;

	uint8_t* inp = reinterpret_cast<uint8_t*>(content);
	uint8_t output[size*4];

	if(!decode(Slice<uint8_t>(inp, size), Slice<uint8_t>(output, size*4))) {
		std::cout << "Failed to decompress input: " << compressed << std::endl;
	}
}
