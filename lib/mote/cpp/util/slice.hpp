/**
 * slice.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef SLICE_HPP
#define SLICE_HPP

#include <cstddef>
#include <algorithm>	// min/max
#include <limits>

namespace awap {

template<typename T>
struct Slice
{
	Slice(T* ptr, size_t len) : data(ptr), length(len) {}
	Slice(std::remove_const<T>* ptr, size_t len) : data(ptr), length(len) {}
	Slice(const Slice<typename std::remove_const<T>::type>& other) : data(other.data), length(other.length) {}

	T* data;
	size_t length;

	inline bool isEmpty() const {
		return !(length > 0);
	}

	inline void increment() {
		++data;
		--length;
	}

	template<size_t N>
	inline size_t write(const T(&src)[N]) {
		const size_t nn = (N < length)? N : length;
		for(size_t ii = 0; ii < nn; ++ii) {
			data[ii] = src[ii];
		}
		data += nn;
		length -= nn;
		return nn;
	}

	inline Slice<T> sub(const int start = 0, const int end = std::numeric_limits<int>::max()) const {
		size_t norm_start = normalizeIndex(start);
		size_t norm_end   = normalizeIndex(end);
		if(norm_start > norm_end) {
			return Slice<T>(static_cast<T*>(nullptr), 0);
		} else {
			return Slice<T>(data + norm_start, norm_end - norm_start);
		}
	}

private:
	// TODO: fix index type for realy big slices
	inline size_t normalizeIndex(const int index) const {
		if(index >= 0) {
			return static_cast<size_t>(std::min(static_cast<int>(length), index));
		} else {
			return static_cast<size_t>(std::max(0, index + static_cast<int>(length)));
		}
	}
};

template<typename T>
inline bool operator==(const Slice<T>& s0, const Slice<T>& s1)
{
	if(s0.length != s1.length) {
		return false;
	}
	for(size_t ii = 0; ii < s0.length; ++ii) {
		if(s0.data[ii] != s1.data[ii]) {
			return false;
		}
	}
	return true;
}

template<typename T, size_t N>
inline Slice<T> slice(T(&ptr)[N])
{
	Slice<T> sl(ptr, N);
	return sl;
}

template<typename T>
inline Slice<T> slice(T* ptr, size_t len)
{
	Slice<T> sl(ptr, len);
	return sl;
}

} // namespace awap

#endif // SLICE_HPP
