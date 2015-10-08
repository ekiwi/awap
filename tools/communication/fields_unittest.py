#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# fields_unittest.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>


import unittest
from fields import Byte, Field, CodeGenerator, InOrderPlacement, ByteBoundarySortPlacement

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
		self.assertEqual(f.size_in_byte(bytes[0]), 7)
		# in bytes[1]: FFFFF000
		self.assertEqual(f.msb_in_byte(bytes[1]), 7)
		self.assertEqual(f.lsb_in_byte(bytes[1]), 3)
		self.assertEqual(f.size_in_byte(bytes[1]), 5)

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
		self.assertEqual(b.index, 0)
		b1 = Byte(1)
		self.assertEqual(b1.index, 1)

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

class TestCodeGeneration(unittest.TestCase):
	def setUp(self):
		self.cg = CodeGenerator(data_src="data", field_prefix="pre->")

	def test_marshal(self):
		b = Byte()
		f = Field("test", 4)
		self.assertTrue(f.place(b, 3))
		# for marshalling we need the bytes, not the field
		self.assertRaises(AssertionError, self.cg.marshal, f)
		self.assertEqual(self.cg.marshal(b), "data[ 0] = (pre->test << 0);")
		self.assertTrue(Field("test2", 2).place(b,5))
		self.assertEqual(self.cg.marshal(b), "data[ 0] = (pre->test2 << 4) | (pre->test << 0);")

	def test_unmarshal(self):
		b0 = Byte(0)
		b1 = Byte(1)
		f0 = Field("test", 4)
		f1 = Field("test2", 8)
		self.assertTrue(f0.place(b1, 3))
		# for unmarshalling we need the field, not the byte
		self.assertRaises(AssertionError, self.cg.unmarshal, b1)
		self.assertEqual(self.cg.unmarshal(f0), "pre->test = ((data[ 1] >> 0) & 0x0f) << 0;")
		self.assertTrue(f1.place([b0, b1], 11))
		self.assertEqual(self.cg.unmarshal(f1), "pre->test2 = ((data[ 0] >> 0) & 0x0f) << 4 | ((data[ 1] >> 4) & 0x0f) << 0;")

class TestPlacement(unittest.TestCase):
	def test_in_order_placement(self):
		pp = InOrderPlacement()
		f0 = Field("f0", 4)
		f1 = Field("f1", 5)
		f2 = Field("f2", 12)
		f3 = Field("f3", 2)
		f4 = Field("f4", 32)
		fields = [f0, f1, f2, f3, f4]
		bytes = pp.place(fields)
		self.assertEqual(len(bytes), 7)
		self.assertEqual(f0.msb_in_byte(bytes[0]), 7)
		self.assertEqual(f0.lsb_in_byte(bytes[0]), 4)
		self.assertEqual(f1.msb_in_byte(bytes[0]), 3)
		self.assertEqual(f1.lsb_in_byte(bytes[1]), 7)
		self.assertEqual(f2.msb_in_byte(bytes[1]), 6)
		self.assertEqual(f2.lsb_in_byte(bytes[2]), 3)
		self.assertEqual(f3.msb_in_byte(bytes[2]), 2)
		self.assertEqual(f3.lsb_in_byte(bytes[2]), 1)
		self.assertEqual(f4.msb_in_byte(bytes[2]), 0)
		self.assertEqual(f4.lsb_in_byte(bytes[6]), 1)

	def test_byte_boundary_sort_placement(self):
		pp = ByteBoundarySortPlacement()
		f0 = Field("a", 4)
		f1 = Field("c", 7)
		f2 = Field("b0", 1)
		f3 = Field("d", 5)
		f4 = Field("e", 3)
		f5 = Field("big", 32)
		f6 = Field("b3", 1)
		fields = [f0, f1, f2, f3, f4, f5, f6]
		front_field = Field("first_id", 5)
		bytes = pp.place(fields, front_field=front_field)
		self.assertEqual(len(bytes), 7)
		self.assertEqual(front_field.msb_in_byte(bytes[0]), 7)
		self.assertEqual(front_field.lsb_in_byte(bytes[0]), 3)
		self.assertEqual(f4.msb_in_byte(bytes[0]), 2)
		self.assertEqual(f4.lsb_in_byte(bytes[0]), 0)
		# 32bit data
		self.assertEqual(f5.msb_in_byte(bytes[1]), 7)
		self.assertEqual(f5.lsb_in_byte(bytes[1]), 0)
		self.assertEqual(f5.msb_in_byte(bytes[2]), 7)
		self.assertEqual(f5.lsb_in_byte(bytes[2]), 0)
		self.assertEqual(f5.msb_in_byte(bytes[3]), 7)
		self.assertEqual(f5.lsb_in_byte(bytes[3]), 0)
		self.assertEqual(f5.msb_in_byte(bytes[4]), 7)
		self.assertEqual(f5.lsb_in_byte(bytes[4]), 0)
		#
		self.assertEqual(f2.msb_in_byte(bytes[5]), 7)
		self.assertEqual(f2.lsb_in_byte(bytes[5]), 7)
		self.assertEqual(f1.msb_in_byte(bytes[5]), 6)
		self.assertEqual(f1.lsb_in_byte(bytes[5]), 0)
		self.assertEqual(f6.msb_in_byte(bytes[6]), 5)
		self.assertEqual(f6.lsb_in_byte(bytes[6]), 5)
		self.assertEqual(f3.msb_in_byte(bytes[6]), 4)
		self.assertEqual(f3.lsb_in_byte(bytes[6]), 0)
		self.assertEqual(f0.msb_in_byte(bytes[7]), 3)
		self.assertEqual(f0.lsb_in_byte(bytes[7]), 0)

if __name__ == "__main__":
	unittest.main()
