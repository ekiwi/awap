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
public:
	BitSlice() {}

	inline bool isEmpty() const {
		return true;
	}

	size_t bitCount() const {
		return 0;
	}

	size_t byteCount() const {
		return 0;
	}

	template<size_t N>
	inline size_t writeBits(const uint32_t data) {
		return 0;
	}

	template<size_t N>
	inline uint32_t readBits() {
		return 0;
	}
};


template<typename T, size_t N>
inline BitSlice bit_slice(T(&ptr)[N])
{
	BitSlice sl;
	return sl;
}

template<typename T>
inline BitSlice bit_slice(T* ptr, size_t len)
{
	BitSlice sl;
	return sl;
}

} // namespace awap

#endif // BIT_SLICE_HPP
