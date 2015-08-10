#include <iostream>
#include <fstream>

#include "code.hpp"



int main(int argc, char* argv[]) {
	if(argc < 3 || (argv[1][0] != 'e' && argv[1][0] != 'd')) {
		std::cout << argv[0] << "[e]ncode/[d]ecode INPUT" << std::endl;
		return 1;
	}
	std::string filename(argv[2]);

	std::cout << "input: " << filename << std::endl;

	std::ifstream input(filename, std::ios::in|std::ios::binary|std::ios::ate);
	if(!input.is_open()) {
		std::cout << "could not open " << filename << std::endl;
		return 2;
	}


	size_t size = input.tellg();
	char content[size];
	input.seekg (0, std::ios::beg);
	input.read (content, size);
	input.close();

	std::cout << "read content from " << filename << std::endl;


//	const uint8_t* input = reinterpret_cast<uint8_t*>(content);
//	uint8_t output[size];
//	Huffman::encode(input, output, size);

//	uint8_t decoded_output[size];
//	Huffman::decode(output, decoded_output, size);
}
