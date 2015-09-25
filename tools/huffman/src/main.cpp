/**
 * main.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */


#include <iostream>
#include <fstream>

#include "huffman.hpp"

using namespace huffman;

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
	size_t buffer_size = size*4;
	uint8_t buffer[buffer_size];
	Slice<uint8_t> output(buffer, buffer_size);

	if(!decode(slice(inp, size), output)) {
		std::cout << "Failed to decompress input: " << compressed << std::endl;
		if(output.length == buffer_size) {
			std::cout << "Probably, the output buffer was too small..." << std::endl;
		}
	}

	std::cout << "Decompressed to " << output.length << " bytes." << std::endl;


	if(argc < 3) {
		return 0;
	}


	std::string original(argv[2]);
	std::ifstream orig_file(original, std::ios::in|std::ios::binary|std::ios::ate);
	if(!orig_file.is_open()) {
		std::cout << "could not open " << original << std::endl;
		return 3;
	}

	size_t orig_size = orig_file.tellg();
	char orig_content[orig_size];
	orig_file.seekg (0, std::ios::beg);
	orig_file.read (orig_content, orig_size);
	orig_file.close();

	uint8_t* orig_inp = reinterpret_cast<uint8_t*>(orig_content);

	if(slice(orig_inp, orig_size) == output) {
		std::cout << "Sucess! Decompressed file matches original file (" << original << ")" << std::endl;
	} else {
		std::cout << "Fail! Decompressed file does NOT match original file (" << original << ")" << std::endl;
	}
}
