#ifndef HUFFMAN_HPP
#define HUFFMAN_HPP

#include <algorithm>
#include <array>


struct HuffmanSymbol {
	double p;
	uint32_t value;
	HuffmanSymbol* parent0;	// parent 0 is more likely!
	HuffmanSymbol* parent1;
};


class HuffmanCode {
	using Symbol = std::vector<uint8_t>;
	std::vector<Symbol> symbols;

public:
	void add_symbol(const Symbol& symbol) {
		this->symbols.push_back(symbol);
	}

	void generate(const uint8_t* input, const size_t input_length) {
		// sort special symbols by size
		sort(this->symbols.begin(), this->symbols.end(),
			[](const Symbol a, const Symbol b) -> bool
			{ return a.size() > b.size(); }
		);

		// collect symbol statistics
		size_t count[256 + this->symbols.size()];
		const uint8_t* input_end;
		while(input != input_end) {
			const Symbol* symbol = this->match_symbol(input, input_end);
			++input;
		}
	}


private:
	const Symbol* match_symbol(const uint8_t* first, const uint8_t* last) const {
		for(auto& sym : this->symbols) {
			if((last - first) <= sym.size()) {
				bool match = true;
				for(size_t ii = 0; ii < sym.size(); ++ii) {
					if(first[ii] != sym[ii]) {
						match = false;
						break;
					}
				}
				if(match) {
					return &sym;
				}
			}
		}
		return nullptr;
	}

};

#endif // HUFFMAN_HPP
