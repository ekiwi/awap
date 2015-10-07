#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# new_fields.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

import math
import unittest

class Byte(object):
	def __init__(self):
		self.fields = []
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

class TestFields(unittest.TestCase):
	def test_field_defaults(self):
		f = Field("test", 4)
		self.assertEqual(f.name, "test")
		self.assertEqual(f.size, 4)		# in bits

		# position is yet undefined
		self.assertTrue(isinstance(f.bytes, list))
		self.assertEqual(len(f.bytes), 0)

		# most and least significant bit definitions
		# relative to first/last byte in list
		# if field does not have a position, these should be -1
		self.assertEqual(f.msb, -1)
		self.assertEqual(f.lsb, -1)

		# byte relative msb/lsb are only defined for bytes that the field
		# is placed in
		self.assertEqual(f.msb_in_byte(Byte()), -1)
		self.assertEqual(f.lsb_in_byte(Byte()), -1)

	def test_field_place(self):
		f = Field("test", 4)
		# place Field in single byte, msb = f.size - 1 = 3 (=> lsb should be 0)
		b0 = Byte()
		self.assertTrue(f.place(b0, 3))
		# now the field should have all placement information
		self.assertEqual(len(f.bytes), 1)
		self.assertEqual(f.bytes[0], b0)
		self.assertEqual(f.msb, 3)
		self.assertEqual(f.lsb, 0)

	def test_field_invalid_place(self):
		# try to place Field in single byte, in invalid position
		b1 = Byte()
		self.assertFalse(Field("too_long", 12).place(b1, 7))
		self.assertFalse(Field("overlap_msb", 4).place(b1, 10))
		self.assertFalse(Field("overlap_lsb", 12).place(b1, 2))

		f = Field("test", 4)
		self.assertTrue(f.place(b1, 3))
		# field cannot be placed twice, no matter, what the byte looks like
		b2 = Byte()
		self.assertFalse(f.place(b2, 3))

	def test_field_place_multiple_bytes(self):
		# place long field in two bytes
		bytes = [Byte(), Byte()]
		f = Field("too_long_for_one_byte", 12)
		self.assertTrue(f.place(bytes, 14))
		self.assertEqual(len(f.bytes), 2)
		self.assertEqual(f.bytes[0], bytes[0])
		self.assertEqual(f.bytes[1], bytes[1])
		# msb and lsb are always relative to the underlying byte list
		self.assertEqual(f.msb, 14)
		self.assertEqual(f.lsb, 3)
		# check that bytes know the fields
		self.assertEqual(len(bytes[0].fields), 1)
		self.assertEqual(len(bytes[1].fields), 1)
		self.assertEqual(bytes[0].fields[0], f)
		self.assertEqual(bytes[1].fields[0], f)
		# check relative positions
		# in bytes[0]: 0FFFFFFF
		self.assertEqual(f.msb_in_byte(bytes[0]), 6)
		self.assertEqual(f.lsb_in_byte(bytes[0]), 0)
		# in bytes[1]: FFFFF000
		self.assertEqual(f.msb_in_byte(bytes[1]), 7)
		self.assertEqual(f.lsb_in_byte(bytes[1]), 3)

		# place one field in more bytes than needed
		bytes2 = [Byte(), Byte(), Byte()]
		f2 = Field("too_long_for_one_byte", 12)
		self.assertTrue(f2.place(bytes2, 23))
		self.assertEqual(len(f2.bytes), 2)
		self.assertEqual(f2.bytes[0], bytes2[0])
		self.assertEqual(f2.bytes[1], bytes2[1])

		bytes3 = [Byte(), Byte(), Byte()]
		f3 = Field("too_long_for_one_byte", 12)
		self.assertTrue(f3.place(bytes3, 14))
		self.assertEqual(len(f3.bytes), 2)
		self.assertEqual(f3.bytes[0], bytes3[1])
		self.assertEqual(f3.bytes[1], bytes3[2])

	def test_byte_defaults(self):
		b = Byte()
		# a byte maintain references to all fields it holds
		self.assertTrue(isinstance(b.fields, list))
		self.assertEqual(len(b.fields), 0)

	def test_byte_place_single_field(self):
		b = Byte()
		# place a field with lsb = 0 (=> msb = 3)
		f0 = Field("f0", 4)
		self.assertTrue(b.place(f0, 3))
		self.assertEqual(len(b.fields), 1)
		self.assertEqual(b.fields[0], f0)
		# field remains unaffected
		self.assertEqual(f0.msb, -1)
		self.assertEqual(f0.lsb, -1)
		self.assertEqual(f0.size, 4)
		self.assertEqual(len(f0.bytes), 0)

	def test_byte_can_place(self):
		b = Byte()
		f0 = Field("f0", 4)
		self.assertTrue(b.can_place(f0, 3))
		# byte remaons unaffected
		self.assertEqual(len(b.fields), 0)
		# field remains unaffected
		self.assertEqual(f0.msb, -1)
		self.assertEqual(f0.lsb, -1)
		self.assertEqual(f0.size, 4)
		self.assertEqual(len(f0.bytes), 0)

	def test_byte_place_overlapping(self):
		b = Byte()
		self.assertTrue(b.place(Field("f0", 4), 3))
		# trying to place an overlapping field should fail
		self.assertFalse(b.place(Field("fail", 4), 3))	# bit3 is occupied by f0

	def test_byte_place_multibyte_field(self):
		b = Byte()
		# placing fields, that occupy multiple bytes is fine
		self.assertTrue(b.place(Field("f2", 4), 0))
		self.assertTrue(b.place(Field("f3", 4), 10))

	def test_byte_place_out_of_byte(self):
		# trying to place a field that will not be contained in the current byte
		# should return false and leave the byte unaffected
		b = Byte()
		self.assertFalse(b.place(Field("f3", 4), 11))
		self.assertFalse(b.place(Field("f3", 4), -1))
		self.assertTrue(isinstance(b.fields, list))
		self.assertEqual(len(b.fields), 0)


if __name__ == "__main__":
	unittest.main()
