/**
 * util.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef UTIL_HPP
#define UTIL_HPP

#include <cstddef>
#include <cstring>	// std::strlen
#include <type_traits>	// std::is_integral
#include <hpp/ostfriesentee.hpp>	// ostfriesentee::String
#include <awap.hpp>		// Runtime::panic, Runtime::warn
#include <util/slice.hpp>
#include <util/bit_slice.hpp>

namespace awap {

template<typename T, size_t N>
static constexpr inline size_t
arrayCount(T (&)[N]) { return N; }


template<typename T0, typename T1>
static constexpr inline T0
divideCeil(const T0& dividend, const T1& divisor)
{
	static_assert(std::is_integral<T0>::value, "divideCeil only works for integer types.");
	static_assert(std::is_integral<T1>::value, "divideCeil only works for integer types.");
	return (dividend + divisor - 1) / divisor;
}

class String : public ostfriesentee::String
{
public:
	String(char* data) : ostfriesentee::String(data, std::strlen(data)) {}
	String(char* data, uint16_t length) : ostfriesentee::String(data, length) {}
	String(const dj_di_pointer data, uint16_t length) : ostfriesentee::String(data, length) {}
};

static inline void assert(const bool expression, Panic panic) {
	if(!expression) {
		Runtime::panic(panic);
	}
}

static inline bool check(const bool expression, Warning warn) {
	if(!expression) {
		Runtime::warn(warn);
		return false;
	} else {
		return true;
	}
}

} // namespace awap

#endif // UTIL_HPP
