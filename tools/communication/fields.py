#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# fiels.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

import math

class Field(object):
	def __init__(self, name, bits):
		self.name = name
		self.bits = bits

	def __str__(self):
		return "#" * self.bits

	def __repr__(self):
		return str(self)

class Byte(object):
	def __init__(self, field=None):
		self.free_bits = 8
		self.fields = []
		self.bytes = 0	#additional bytes to hold fields with bits > 8
		if isinstance(field, Field):
			self.insert(field)


	def insert(self, field):
		additional_bytes_needed = int(math.ceil(field.bits / 8.0)) - 1
		bits_needed = field.bits - (additional_bytes_needed * 8)
		if(bits_needed > self.free_bits):
			return False
		if additional_bytes_needed > 0:
			if self.bytes > 0:
				return False
			else:
				self.bytes = additional_bytes_needed
		self.free_bits -= bits_needed
		self.fields.append(field)
		return True

def sort(fields):
	print(fields)
	fields = sorted(fields, key=lambda field: -field.bits)
	print(fields)
	bytes = []
	for field in fields:
		print(field)
		for byte in bytes:
			if byte.insert(field):
				field = None
				break
		if field:
			bytes.append(Byte(field))
	return bytes


if __name__ == "__main__":
	fields = []
	fields.append(Field("a", 4))
	fields.append(Field("c", 7))
	fields.append(Field("b0", 1))
	fields.append(Field("d", 5))
	fields.append(Field("e", 3))
	fields.append(Field("f", 2))
	fields.append(Field("b1", 1))
	fields.append(Field("g", 8))
	fields.append(Field("h", 5))
	fields.append(Field("i", 3))
	fields.append(Field("b2", 1))
	fields.append(Field("j", 5))
	fields.append(Field("k", 5))
	fields.append(Field("l", 2))
	fields.append(Field("m", 12))
	fields.append(Field("n", 17))
	fields.append(Field("b3", 1))

	bytes = sort(fields)
	byte_count = sum((1 + b.bytes) for b in bytes)

	bits = sum(f.bits for f in fields)

	print("Could fit {} bits ({} bytes) into {} bytes => {}%.".format(
		bits, bits / 8.0, byte_count, int(byte_count / (bits / 8.0) * 100)))
