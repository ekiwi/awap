#ifndef UTIL_HPP
#define UTIL_HPP

#include <cstddef>
#include <util/slice.hpp>

namespace awap {

template<typename T, size_t N>
static constexpr inline size_t
arrayCount(T (&)[N]) { return N; }

} // namespace awap

#endif // UTIL_HPP
