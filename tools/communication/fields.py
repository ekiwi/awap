#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# fiels.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>


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
		if isinstance(field, Field):
			self.insert(field)


	def insert(self, field):
		if(field.bits > self.free_bits):
			return False
		else:
			self.free_bits -= field.bits
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
	fields.append(Field("b3", 1))

	bytes = sort(fields)

	bits = sum(f.bits for f in fields)

	print("Could fit {} bits ({} bytes) into {} bytes => {}%.".format(
		bits, bits / 8.0, len(bytes), int(len(bytes) / (bits / 8.0) * 100)))
