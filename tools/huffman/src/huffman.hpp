#ifndef HUFFMAN_HPP
#define HUFFMAN_HPP

#include <stdint.h>
#include "slice.hpp"

namespace huffman {

bool decode(const Slice<uint8_t>& input, Slice<uint8_t>& output);

} // namspace huffman

#endif // HUFFMAN_HPP
