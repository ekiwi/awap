#ifndef UTIL_HPP
#define UTIL_HPP

#include <cstddef>
#include <cstring>	// std::strlen
#include <type_traits>	// std::is_integral

#include <hpp/ostfriesentee.hpp>	// ostfriesentee::String

#include <util/slice.hpp>

namespace awap {

template<typename T, size_t N>
static constexpr inline size_t
arrayCount(T (&)[N]) { return N; }


template<typename T>
static constexpr inline T
divideCeil(const T& dividend, const T& divisor)
{
	static_assert(std::is_integral<T>::value, "divideCeil only works for integer types.");
	return (dividend + divisor - 1) / divisor;
}

class String : public ostfriesentee::String
{
public:
	String(char* data) : ostfriesentee::String(data, std::strlen(data)) {}
	String(char* data, uint16_t length) : ostfriesentee::String(data, length) {}
	String(const dj_di_pointer data, uint16_t length) : ostfriesentee::String(data, length) {}
};

} // namespace awap

#endif // UTIL_HPP
