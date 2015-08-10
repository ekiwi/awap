#include <iostream>
#include <fstream>

#include "code.hpp"



int main(int argc, char* argv[]) {
	if(argc < 2) {
		std::cout << argv[0] << " COMPRESSED [ORIGINAL]" << std::endl;
		return 1;
	}
	std::string compressed(argv[2]);

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

	


//	const uint8_t* input = reinterpret_cast<uint8_t*>(content);
//	uint8_t output[size];
//	Huffman::encode(input, output, size);

//	uint8_t decoded_output[size];
//	Huffman::decode(output, decoded_output, size);
}
