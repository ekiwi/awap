/**
 * bit_slice.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef BIT_SLICE_HPP
#define BIT_SLICE_HPP

#include <util/slice.hpp>

namespace awap {

class BitSlice
{
	// either `uint8_t` or `const uint8_t`
	using T = uint8_t;
public:
	BitSlice(T* ptr, size_t len) : bytes(ptr, len) {}
	BitSlice(const Slice<T>& bytes) : bytes(bytes) {}

	inline bool isEmpty() const {
		return bytes.isEmpty();
	}

	size_t bitCount() const {
		return (8u * bytes.length) - bitsRead;
	}

	size_t byteCount() const {
		return bytes.length;
	}

	template<size_t N>
	inline size_t writeBits(const uint32_t data) {
		return 0;
	}

	template<size_t N>
	inline uint32_t readBits() {
		if(N - bitsAvailable <= 0) {
			const uint8_t mask = (1 << bitsAvailable) - 1;
			uint32_t result = bytes.data[0]  >> (bitsAvailable - N)
		}
		uint32_t result = tempByte;

		return 0;
	}
private:
	Slice<T> bytes;
	uint8_t bitsAvailable = 8;
	uint8_t tempByte;
};


template<typename T, size_t N>
inline BitSlice bit_slice(T(&ptr)[N])
{
	BitSlice sl(ptr, N);
	return sl;
}

template<typename T>
inline BitSlice bit_slice(T* ptr, size_t len)
{
	BitSlice sl(ptr, len);
	return sl;
}

} // namespace awap

#endif // BIT_SLICE_HPP
