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
		self.id = -1			# nth field in byte
		self.place_last = False		# placement **hint**

	def place(self, id, byte, bit):
		self.id = id
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

	def cpp_get_byte(self, byte_id, prefix=""):
		shift = self.pos_bit - (self.additional_byte_count - byte_id) * 8
		cpp = "(({value} & {mask})".format(value=prefix + self.name, mask=self.full_mask)
		if shift >= 0:
			cpp += " << {:2})".format(shift)
		else:
			cpp += " >> {:2})".format(-shift)
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
		self.pos = -1
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
		self.pos = pos
		# place fields from LSB to MSB
		bit = 0
		# make sure that field with bits > 8 are placed at the LSB
		fields = sorted(self.fields, key=lambda field: -field.bits + 100 * field.place_last)
		field_id = 0
		for f in fields:
			bit += f.place(id=field_id, byte=self.pos, bit=bit)
			field_id += 1
		# return position of next byte
		return self.pos + 1 + self.bytes

	def cpp_write(self, data="data", prefix=""):
		cpp = "{data}[{byte:2}] = ".format(data=data, byte=self.pos)
		fields = sorted(self.fields, key=lambda field: -field.pos_bit)
		cpp += " | ".join(ff.cpp_get_byte(0, prefix) for ff in fields) + ";"
		for ii in range(1, self.bytes + 1):
			cpp += "\n{data}[{byte:2}] = ({value} >> ({shift} * 8) & 0xff;".format(
				data=data,
				byte=self.pos + ii,
				value=prefix + self.fields[0].name,
				shift=self.fields[0].additional_byte_count - ii)
		return cpp

class Fields(object):
	""" main class, generated C++ code from fields """
	def __init__(self, data_src="data", field_prefix=""):
		self.data_src = data_src
		self.field_prefix = field_prefix
		self.fields = []
		self.bytes = []
		self.front_field = None

	def set_front_field(self, name, bits):
		assert(isinstance(name, str))
		bits = int(bits)
		assert(bits > 0)
		self.front_field = Field(name, bits)
		self.front_field.place_last = True

	def add_field(self, name, bits):
		assert(isinstance(name, str))
		bits = int(bits)
		assert(bits > 0)
		self.fields.append(Field(name, bits))

	def to_dict(self):
		(fields, bytes) = self._sort_and_place()
		from_data = "\n".join(
			ff.cpp_read(self.data_src, self.field_prefix) for ff in fields)
		if self.front_field:
			from_data = self.front_field.cpp_read(
				self.data_src, self.field_prefix) + "\n" + from_data
		to_data = "\n".join(
			bb.cpp_write(self.data_src, self.field_prefix) for bb in bytes)
		byte_count = sum((1 + b.bytes) for b in bytes)
		return {
			'unmarshal': from_data,
			'marshal': to_data,
			'bytes': byte_count,
		}

	def _sort_and_place(self):
		fields = sorted(self.fields, key=lambda field: -field.bits)
		bytes = []
		if self.front_field:
			self.front_field.place_last = True
			bytes.append(Byte(self.front_field))
		for field in fields:
			for byte in bytes:
				if byte.insert(field):
					field = None
					break
			if field:
				bytes.append(Byte(field))
		# place
		pos = 0
		for bb in bytes:
			pos = bb.place(pos=pos)
		# sort by position
		fields = sorted(fields, key=lambda field: field.pos_byte)
		return (fields, bytes)

if __name__ == "__main__":
	fields = Fields()
	fields.add_field("a", 4)
	fields.add_field("c", 7)
	fields.add_field("b0", 1)
	fields.add_field("d", 5)
	fields.add_field("e", 3)
	fields.add_field("f", 2)
	fields.add_field("b1", 1)
	fields.add_field("g", 8)
	fields.add_field("h", 5)
	fields.add_field("i", 3)
	fields.add_field("b2", 1)
	fields.add_field("j", 5)
	fields.add_field("k", 5)
	fields.add_field("l", 2)
	fields.add_field("m", 12)
	fields.add_field("n", 17)
	fields.add_field("b3", 1)
	fields.set_front_field("first_id", 5)

	dd = fields.to_dict()
	print("\nunmarshal:\n{}".format(dd['unmarshal']))
	print("\nmarshal:\n{}".format(dd['marshal']))
	print("\nbytes:\n{}".format(dd['bytes']))

	# TODO: reenable statistics
	#print("Could fit {} bits ({} bytes) into {} bytes => {}%.".format(
	#	bits, bits / 8.0, byte_count, int(byte_count / (bits / 8.0) * 100)))
