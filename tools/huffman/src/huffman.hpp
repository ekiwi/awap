/**
 * huffman.hpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#ifndef HUFFMAN_HPP
#define HUFFMAN_HPP

#include <stdint.h>
#include <util/slice.hpp>

namespace huffman {

bool decode(const awap::Slice<uint8_t>& input, awap::Slice<uint8_t>& output);

} // namspace huffman

#endif // HUFFMAN_HPP
