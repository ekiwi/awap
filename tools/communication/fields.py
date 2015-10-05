#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# fiels.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

import math

class Field(object):
	def __init__(self, name, bits):
		self.name = name
		self.bits = bits
		self.pos_byte = -1
		self.pos_bit = -1		# LSB

	def place(self, byte, bit):
		self.pos_byte = byte
		self.pos_bit = bit		# LSB
		return self.leading_bits

	@property
	def bytes(self):
		return int(math.ceil(self.bits / 8.0))

	@property
	def additional_byte_count(self):
		return self.bytes - 1

	@property
	def leading_bits(self):
		return self.bits - (self.additional_byte_count * 8)

	@property
	def byte_mask(self):
		return "{:#04x}".format((1 << self.leading_bits) - 1)

	@property
	def full_mask(self):
		return "{value:#0{zeros}x}".format(
			value=(1 << self.bits) - 1,
			zeros=(2 + 2 * self.bytes))

	def cpp_read(self, data="data", prefix=""):
		cpp = "{value:{padding}} = (({data}[{byte:2}] >> {bit}) & {mask})".format(
			value=prefix + self.name,
			padding=10,
			data=data,
			byte=self.pos_byte,
			bit=self.pos_bit,
			mask=self.byte_mask)
		for ii in range(0, self.additional_byte_count):
			cpp += " << ({shift} * 8) | {data}[{byte}]".format(
				shift=self.additional_byte_count - ii,
				data=data,
				byte=ii+self.pos_byte + 1)
		return cpp + ";"

	def cpp_write(self, data="data", prefix=""):
		cpp = "auto temp = ({value} & {full_mask});\n".format(
			value=prefix + self.name,
			padding=10,
			full_mask=self.full_mask)
		shift = self.pos_bit - (self.additional_byte_count * 8);
		cpp += "{data}[{byte:2}] = {data}[{byte:2}] & ({mask} << {bit}) | temp".format(
			data=data,
			byte=self.pos_byte,
			bit=self.pos_bit,
			mask=self.byte_mask)
		if shift >= 0:
			cpp += " << {:2};".format(shift)
		else:
			cpp += " >> {:2};".format(-shift)
		for ii in range(0, self.additional_byte_count):
			cpp += "\n{data}[{byte:2}] = (temp >> ({shift} * 8)) & 0xff;".format(
				shift=self.additional_byte_count - ii - 1,
				data=data,
				byte=ii+self.pos_byte + 1)
		#cpp = "{value:10} = (({data}[{byte:2}] >> {bit}) & {mask})"
		return cpp

	def __str__(self):
		s = "{:<8}".format(self.name) + "#" * self.bits
		if self.pos_bit >= 0:
			s += "[]"
		return s

	def __repr__(self):
		return self.name + ": " + "#" * self.bits

class Byte(object):
	def __init__(self, field=None):
		self.free_bits = 8
		self.fields = []
		self.bytes = 0	#additional bytes to hold fields with bits > 8
		if isinstance(field, Field):
			self.insert(field)


	def insert(self, field):
		if(field.leading_bits > self.free_bits):
			return False
		if field.additional_byte_count > 0:
			if self.bytes > 0:
				return False
			else:
				self.bytes = field.additional_byte_count
		self.free_bits -= field.leading_bits
		self.fields.append(field)
		return True

	def place(self, pos):
		""" propagates placement information to the fields """
		# place fields from LSB to MSB
		bit = 0
		# make sure that field with bits > 8 are placed at the LSB
		fields = sorted(self.fields, key=lambda field: -field.bits)
		for f in fields:
			bit += f.place(byte=pos, bit=bit)
		# return position of next byte
		return pos + 1 + self.bytes

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

	pos = 0
	for bb in bytes:
		pos = bb.place(pos=pos)

	fields = sorted(fields, key=lambda field: field.pos_byte)
	for ff in fields:
		print(ff.cpp_read())
	print()
	for ff in fields:
		print(ff.cpp_write())

	byte_count = sum((1 + b.bytes) for b in bytes)
	bits = sum(f.bits for f in fields)

	print("Could fit {} bits ({} bytes) into {} bytes => {}%.".format(
		bits, bits / 8.0, byte_count, int(byte_count / (bits / 8.0) * 100)))
