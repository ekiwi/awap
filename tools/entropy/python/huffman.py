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
			'lenght': len(self.value),
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
		dd = {'map': [s.to_dict() for s in self.symbols] }
		dd['max_code_bits'] = max([len(s.code) for s in self.symbols])

	def print_symbols(self):
		symbols = sorted(self.symbols, key=lambda s: -s.p)
		print('\n'.join([str(s) for s in symbols]))

	def print_compression_statistics(self, inp):
		# FIXME: very hacky right now! resets count in symbols...
		for s in self.symbols: s.count = 0
		self.count_symbols(inp)
		old_size = sum([len(s.value) * s.count  for s in self.symbols])
		new_size = sum([len(s.code) * s.count for s in self.symbols]) / 8.0
		print("Size: {} => {} ({:.2%})".format(old_size, new_size, new_size / old_size))


if __name__ == "__main__":
	import os

	hc = HuffmanCode()

	files = ['../../../examples/simple/build/ostfriesentee/app/TemperatureSensor/TemperatureSensor.di',
		'../../../examples/simple/build/ostfriesentee/app/SimpleTemperatureSubscriber/SimpleTemperatureSubscriber.di']

	for filename in files: 
		with open(filename, 'rb') as ff:
			inp = ff.read()
		hc.count_symbols(inp)

	hc.generate()

	hc.print_symbols()

	for filename in files: 
		with open(filename, 'rb') as ff:
			inp = ff.read()
		print(os.path.basename(filename))
		hc.print_compression_statistics(inp)

	hc.to_dict()
