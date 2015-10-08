#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# fields.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

import math

class Byte(object):
	def __init__(self, index=0):
		assert(isinstance(index, int))
		self.fields = []
		self.index = index
		self._bits = [0] * 8

	def place(self, field, msb, dry_run=False):
		assert(isinstance(field, Field))
		# calculate msb and lsb in the local (Byte) context
		local_msb = min(msb, 7)
		local_lsb = max(msb - field.size + 1, 0)
		local_size = local_msb - local_lsb + 1
		if local_size <= 0:
			return False	# nothing to insert
		# check if space available
		if sum(self._bits[local_lsb:local_msb + 1]) > 0:
			return False	# error: overlapping with already place field
		if not dry_run:
			self._bits[local_lsb:local_msb + 1] = [1] * local_size
			self.fields.append(field)
		return True

	def can_place(self, field, msb):
		return self.place(field=field, msb=msb, dry_run=True)

class Field(object):
	def __init__(self, name, size):
		assert(isinstance(name, str))
		assert(isinstance(size, int))
		assert(size > 0)
		self.name = name
		self.bytes = []
		# size is immutable
		self._size = size
		self._msb = -1

	@property
	def size(self):
		return self._size

	@property
	def msb(self):
		return self._msb

	@property
	def lsb(self):
		if self._msb == -1:	return -1
		else: return self._msb + 1 - self.size

	def _bit_offset(self, byte):
		return (len(self.bytes) - self.bytes.index(byte) - 1) * 8

	def msb_in_byte(self, byte):
		assert(isinstance(byte, Byte))
		if not byte in self.bytes:
			return -1
		return min(self.msb - self._bit_offset(byte), 7)

	def lsb_in_byte(self, byte):
		assert(isinstance(byte, Byte))
		if not byte in self.bytes:
			return -1
		return max(self.lsb - self._bit_offset(byte), 0)

	def size_in_byte(self, byte):
		assert(isinstance(byte, Byte))
		if not byte in self.bytes:
			return -1
		return self.msb_in_byte(byte) - self.lsb_in_byte(byte) + 1

	def place(self, bytes, msb):
		if self._msb > -1 or len(self.bytes) > 0:
			return False	# already placed

		if isinstance(bytes, Byte):
			bytes = [bytes]
		assert(isinstance(bytes, list))
		assert(isinstance(bytes[0], Byte))

		max_msb = (len(bytes) * 8) - 1
		if msb > max_msb:
			return False	# field does not fit into bytes

		lsb = msb + 1 - self._size
		if lsb < 0:
			return False	# field does not fit into bytes

		# remove not needed bytes from list
		remove_leading_byte_count = len(bytes) - ((msb / 8) + 1)
		remove_trailing_byte_count = lsb / 8
		if remove_trailing_byte_count > 0:
			bytes = bytes[remove_leading_byte_count:-remove_trailing_byte_count]
		else:
			bytes = bytes[remove_leading_byte_count:]
		msb -= remove_trailing_byte_count * 8
		lsb -= remove_trailing_byte_count * 8

		# check if bytes have space
		byte_msb = [(msb % 8) + 8 * ii for ii in range(0, len(bytes))]
		if not all(bb.can_place(self, msb) for bb, msb in zip(bytes, byte_msb)):
			return False	# not all bytes can contain the value

		# place field in bytes
		for bb, msb in zip(bytes, byte_msb):
			bb.place(self, msb)

		self.bytes = list(bytes)	# shallow copy
		self._msb = msb
		return True		# success


class CodeGenerator(object):
	def __init__(self, data_src="data", field_prefix=""):
		assert(isinstance(data_src, str))
		assert(isinstance(field_prefix, str))
		self.data_src = data_src
		self.field_prefix = field_prefix

	def _read_and_shift_field(self, field, byte):
		cpp = "({name} << {lsb})".format(
			name=self.field_prefix + field.name,
			lsb=field.lsb_in_byte(byte))
		return cpp

	def marshal(self, byte):
		assert(isinstance(byte, Byte))
		cpp = "{data}[{index:2}] = ".format(data=self.data_src, index=byte.index)
		fields = sorted(byte.fields, key=lambda field: -field.lsb_in_byte(byte))
		cpp += " | ".join(self._read_and_shift_field(ff, byte) for ff in fields) + ";"
		return cpp

	def _read_and_shift_byte(self, byte, field):
		cpp = "(({data}[{index:2}] >> {lsb}) & 0x{mask}) << {offset}".format(
			data=self.data_src,
			index=byte.index,
			lsb=field.lsb_in_byte(byte),
			mask="{:02x}".format((1 << field.size_in_byte(byte)) - 1),
			offset=field.lsb - field.lsb_in_byte(byte))
		return cpp

	def unmarshal(self, field):
		assert(isinstance(field, Field))
		cpp = "{name} = ".format(name=field.name)
		cpp += " | ".join(self._read_and_shift_byte(bb, field) for bb in field.bytes) + ";"
		return cpp


class InOrderPlacement(object):
	def place(self, fields):
		if not isinstance(fields, list):
			fields = [fields]
		total_size = sum(ff.size for ff in fields)
		byte_count = int(math.ceil(total_size / 8.0))
		bytes = [Byte(ii) for ii in range(0, byte_count)]
		msb = (byte_count * 8) - 1
		for field in fields:
			field.place(bytes, msb)
			msb -= field.size
		return bytes

class ByteBoundarySortPlacement(object):
	def place(self, fields, front_field=None):
		if not isinstance(fields, list):
			fields = [fields]
		if front_field:
			assert(front_field in fields)
		# sort fields, biggest fields first
		fields = sorted(fields, key=lambda field: -field.size)
		# allocate bytes for the worst case
		worst_byte_count = sum(int(math.ceil(ff.size / 8.0)) for ff in fields) + 1
		bytes = [Byte(ii) for ii in range(0, worst_byte_count)]
		if front_field:
			front_field.place(bytes, (worst_byte_count * 8) - 1)
		return bytes
