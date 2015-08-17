#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# huffman.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

"""
"""

import string

def bitstring_to_int(string):
	value = 0
	for cc in string:
		value = value << 1
		if cc == '1':
			value = value | 1
	return value

class HuffmanTouple(object):
	""" Code/Value touple of a HuffmanCode
	"""
	def __init__(self, leaf):
		assert(isinstance(leaf, HuffmanLeaf))
		self.value = leaf.value
		self.code  = leaf.code

class HuffmanLeaf(object):
	""" Represents a symbol of the source langugage
	"""
	def __init__(self, value):
		self.value = value
		self.count = 0
		self.p = 0.0
		self.code = None

	def propagate_code(self, code):
		self.code = code

	def __str__(self):
		if len(self.value) == 1:
			value = '0x{:02X}'.format(ord(self.value))
		else:
			value = self.value
		percentage = '({:.2%})'.format(self.p)
		rr = '"{:<12}": {:4} {:>8}'.format(value, self.count, percentage)
		if self.code is None:
			return rr
		else:
			return '{} => {:>16} ({:2}bit)'.format(rr, self.code, len(self.code))

	def to_dict(self):
		dd = {}
		dd['value'] = {
			'length': len(self.value),
			'data': ['0x{:02X}'.format(ord(cc)).lower() for cc in self.value]}
		dd['code'] = {
			'length': len(self.code),
			'bits': self.code,
			'int': bitstring_to_int(self.code),
			'hex': '0x{:02X}'.format(bitstring_to_int(self.code)).lower()}
		return dd

class HuffmanNode(object):
	def __init__(self, p0, p1):
		self.value = None
		self.count = p0.count + p1.count
		self.p = p0.p + p1.p
		if p0.p > p1.p:
			self.parent_more_likely = p0
			self.parent_less_likely = p1
		else:
			self.parent_more_likely = p1
			self.parent_less_likely = p0

	def propagate_code(self, code):
		self.parent_more_likely.propagate_code("0" + code)
		self.parent_less_likely.propagate_code("1" + code)


class HuffmanCode(object):
	def __init__(self):
		# will be added to count when calculating distribution
		self.base_count = 0.01
		self.symbols = [HuffmanLeaf(chr(ii)) for ii in range(256)]
		self.add_symbol('base')
		self.add_symbol('util')
		self.add_symbol('Temperature')
		self.add_symbol('OBJECT')
		self.add_symbol('awap-common')


	def add_symbol(self, symbol):
		if isinstance(symbol, HuffmanLeaf):
			self.symbols.append(symbol)
		else:
			self.symbols.append(HuffmanLeaf(symbol))

	def count_symbols_in_file(self, filename):
		with open(filename, 'rb') as ff:
			inp = ff.read()
		self.count_symbols(inp)

	def count_symbols(self, inp):
		# sort symbols
		sorted_symbols = sorted(self.symbols, key=lambda s: -len(s.value))

		# loop over file, trying to find symbols in a greedy manner
		# NOTE: especially the way we treat the regular bytes as 'symbols'
		#       makes this not ver efficient
		#       however: we do not really care, since this will only be done
		#       once
		ii = 0
		length = len(inp)
		while ii < length:
			old_ii = ii
			for symbol in sorted_symbols:
				if len(symbol.value) <= ii + length:
					if inp[ii:ii+len(symbol.value)] == symbol.value:
						symbol.count += 1
						ii += len(symbol.value)
						break
			if ii == old_ii:
				print("Error: could not match byte 0x{:02X}".format(inp[ii]))
				exit(1)

	def generate(self):
		""" Generates a Huffman code based on the symbols collected
		    by previous calls to count_symbols.
		"""
		# update probabilities
		total_count = sum([s.count for s in self.symbols]) + len(self.symbols) * self.base_count
		for symbol in self.symbols:
			symbol.p = float(symbol.count + self.base_count) / float(total_count)

		# create sorted symbol list
		symbols = sorted(self.symbols, key=lambda s: -s.p)

		while len(symbols) > 1:
			combined = HuffmanNode(symbols.pop(), symbols.pop())
			symbols.append(combined)
			symbols.sort(key=lambda s: -s.p)

		print("Done merging")
		print("Total count: {}\tTotal p: {}".format(symbols[0].count, symbols[0].p))

		# assign code to all leafs
		symbols[0].propagate_code("")

	def to_dict(self):
		""" Returns a dict that contains information about symbols and codes.
		    It can be used to generate encoder/decoder.
		"""
		symbols = sorted(self.symbols, key=lambda s: -s.p)
		dd = {'map': [s.to_dict() for s in symbols] }
		dd['max_code_bits'] = max([len(s.code) for s in self.symbols])
		return dd

	def print_symbols(self):
		symbols = sorted(self.symbols, key=lambda s: -s.p)
		print('\n'.join([str(s) for s in symbols]))

class HuffmanEncoder(object):
	def __init__(self, code):
		assert(isinstance(code, HuffmanCode))
		touples = (HuffmanTouple(sym) for sym in code.symbols)
		self.symbols = sorted(touples, key=lambda s: -len(s.value))

	def compress_file(self, input_filename, output_filename):
		# FIXME: this is very ineficient code ... we build tje
		#        file as a string of 0s and 1s which is terribly
		#        inefficient, but this is python anyways ... so who cares?
		with open(input_filename, 'rb') as ff:
			inp = ff.read()

		# translate symbols
		outp = ""
		ii = 0
		length = len(inp)
		while ii < length:
			old_ii = ii
			for symbol in self.symbols:
				if len(symbol.value) <= ii + length:
					if inp[ii:ii+len(symbol.value)] == symbol.value:
						outp += symbol.code
						ii += len(symbol.value)
						break
			if ii == old_ii:
				print("Error: could not match byte 0x{:02X}".format(inp[ii]))
				exit(1)

		# pad to get bytes
		outp += '0' * (8 - (len(outp) % 8))

		old_size = len(inp)
		new_size = len(outp) / 8
		print("{} ({}bytes) => {} ({}bytes) ({:.2%})".format(
			input_filename, old_size, output_filename, new_size, float(new_size) / old_size))

		self._write_bit_string(output_filename, outp)

	def _write_bit_string(self, filename, bitstr):
		assert(len(bitstr) % 8 == 0)
		bit_count = 0
		value = 0
		with open(filename, 'wb') as ff:
			for bit in bitstr:
				value = value << 1
				if bit == "1":
					value = value | 1
				bit_count += 1
				if bit_count == 8:
					bit_count = 0
					ff.write(chr(value))
					value = 0


if __name__ == "__main__":
	import os

	hc = HuffmanCode()

	files = ['../../../examples/simple/build/ostfriesentee/app/TemperatureSensor/TemperatureSensor.di',
		'../../../examples/simple/build/ostfriesentee/app/SimpleTemperatureSubscriber/SimpleTemperatureSubscriber.di']

	for filename in files: 
		hc.count_symbols_in_file(filename)

	hc.generate()

	hc.print_symbols()

	enc = HuffmanEncoder(hc)

	for filename in files: 
		output = os.path.join('temp', os.path.basename(filename))
		enc.compress_file(filename, output)

	hc.to_dict()
