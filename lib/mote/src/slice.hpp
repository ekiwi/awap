#ifndef SLICE_HPP
#define SLICE_HPP

#include <cstddef>

namespace awap {

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

	template<size_t N>
	inline size_t write(T(&src)[N]) {
		if(length < N) {
			return 0;
		} else {
			for(size_t ii = 0; ii < N; ++ii) {
				data[ii] = src[ii];
			}
			data += N;
			length -= N;
			return N;
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

} // namespace huffman

#endif // SLICE_HPP
