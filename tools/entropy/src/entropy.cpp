/**
 * entropy.cpp
 *
 * Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
 *
 * This file is part of awap.
 */

#include <iostream>
#include <fstream>
#include <cmath>


int main(int argc, char* argv[]) {
	if(argc < 2) {
		std::cout << argv[0] << " [-csv] INPUT" << std::endl;
		return 1;
	}

	bool print_csv = false;
	std::string filename;
	if(argc > 2 and std::string(argv[1]) == "-csv") {
		print_csv = true;
		filename = argv[2];
	} else {
		filename = argv[1];
	}

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

	// calculate entropy
	size_t count[256] = {0};
	for(auto value : content) {
		count[static_cast<uint8_t>(value)]++;
	}

	double entropy = 0;
	for(auto ii = 0; ii < 256; ++ii) {
		double p = static_cast<double>(count[ii]) / static_cast<double>(size);
		if(p > 0) {
			entropy += p * std::log2(p);
		}


		std::cout << ii << ": " << count[ii];
		std::cout << "\t(" << p * 100 << "%)";
		std::cout  << std::endl;
	}
	std::cout << "H = " << (-entropy);
	std::cout << "\t(" << (-entropy * 100.0 / 8.0) << "%)" << std::endl;

	// print values as csv
	if(print_csv) {
		std::cout << std::endl << std::endl;
		std::cout << "sym,p" << std::endl;
		for(uint32_t ii = 0; ii < 256; ++ii) {
			double p = static_cast<double>(count[ii]) / static_cast<double>(size);
			std::cout << ii << "," << p << std::endl;
		}
	}
}
