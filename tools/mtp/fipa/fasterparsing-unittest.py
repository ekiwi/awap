#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# fasterparsing-unittest.py

import unittest

#from pyparsing import Literal, Suppress, Regex, ParseException, And, Or
from fasterparsing import Literal, Suppress, Regex, ParseException, And, Or

class Test(unittest.TestCase):

	def test_Literal(self):
		ll = Literal('hello')
		self.assertEqual(ll.parseString("hello")[0], "hello")
		self.assertRaises(ParseException, ll.parseString, "not hello")

	def test_Suppress(self):
		ll = Suppress('hello')
		self.assertEqual(len(ll.parseString("hello")), 0)
		self.assertRaises(ParseException, ll.parseString, "not hello")

	def test_Regex(self):
		rr0 = Regex(r'[0-9]{4}')
		self.assertEqual(rr0.parseString("0123")[0], "0123")
		self.assertRaises(ParseException, rr0.parseString, "hello")

	def test_And(self):
		aa0 = And([Literal('hello')])
		self.assertEqual(aa0.parseString("hello")[0], "hello")
		aa1 = And([Literal('Tel'), Regex(r'[0-9]{4}')])
		self.assertEqual(list(aa1.parseString("Tel 0123")), ["Tel", "0123"])
		self.assertRaises(ParseException, aa1.parseString, "hello")
		aa2 = And([Suppress('Tel'), Regex(r'[0-9]{4}')])
		self.assertEqual(aa2.parseString("Tel 0123")[0], "0123")

	def test_Or(self):
		oo0 = Or([Literal('hello')])
		self.assertEqual(oo0.parseString("hello")[0], "hello")
		oo1 = Or([Literal('hello'), Literal('world')])
		self.assertEqual(oo1.parseString("hello world")[0], "hello")

if __name__ == "__main__":
	unittest.main()
