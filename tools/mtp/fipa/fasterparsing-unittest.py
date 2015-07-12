#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# fasterparsing-unittest.py

import unittest, datetime

#from pyparsing import Literal, Suppress, Regex, ParseException, And, Or, CaselessKeyword
from fasterparsing import Literal, Suppress, Regex, ParseException, And, Or, CaselessKeyword

class Test(unittest.TestCase):

	def test_Literal(self):
		ll = Literal('hello')
		self.assertEqual(ll.parseString("hello")[0], "hello")
		self.assertRaises(ParseException, ll.parseString, "not hello")

	def test_CaselessKeyword(self):
		ck0 = CaselessKeyword('test')
		self.assertEqual(ck0.parseString("test")[0], "test")
		self.assertEqual(ck0.parseString("Test")[0], "test")
		self.assertEqual(ck0.parseString("teSt")[0], "test")
		self.assertEqual(ck0.parseString("tesT")[0], "test")
		self.assertRaises(ParseException, ck0.parseString, "not test")
		ck1 = And([CaselessKeyword('hello'), Literal('world')])
		self.assertEqual(ck1.parseString("hello world")[0], "hello")
		self.assertEqual(ck1.parseString("heLlo world")[0], "hello")
		self.assertEqual(ck1.parseString("hellO world")[0], "hello")
		self.assertEqual(ck1.parseString("Hello world")[0], "hello")
		self.assertRaises(ParseException, ck1.parseString, "hello World")

	def test_Suppress(self):
		ll = Suppress('hello')
		self.assertEqual(len(ll.parseString("hello")), 0)
		self.assertRaises(ParseException, ll.parseString, "not hello")

	def test_Regex(self):
		rr0 = Regex(r'[0-9]{4}')
		self.assertEqual(rr0.parseString("0123")[0], "0123")
		self.assertRaises(ParseException, rr0.parseString, "hello")

	def parse_DateTime(self, source, location, tokens):
		tok = tokens[0]
		# ignore sign for now
		if tok[:1] in ['+', '-']:
			tok = tok[1:]
		ts = datetime.datetime(
			year = int(tok[0:4]),
			month = int(tok[4:6]),
			day = int(tok[6:8]),
			hour = int(tok[9:11]),
			minute = int(tok[11:13]),
			second = int(tok[13:15]),
			microsecond = int(tok[15:18]) * 1000)
		return ts

	def test_Regex_DateTime(self):
		DateTime = Regex(r'[\+-]?\d{8}T\d{9}[a-zA-Z]?')
		DateTime.setParseAction(self.parse_DateTime)
		ts = datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000)
		self.assertEqual(DateTime.parseString("20150701T143941567")[0], ts)
		self.assertEqual(DateTime.parseString("+20150701T143941567")[0], ts)
		self.assertEqual(DateTime.parseString("-20150701T143941567z")[0], ts)
		self.assertRaises(ParseException, DateTime.parseString, "20150701Z143941567")
		self.assertRaises(ParseException, DateTime.parseString, "d20150701T143941567")
		self.assertRaises(ParseException, DateTime.parseString, "20150d01T143941567")
		self.assertRaises(ParseException, DateTime.parseString, "20150701T14394156")

	def test_And(self):
		aa0 = And([Literal('hello')])
		self.assertEqual(aa0.parseString("hello")[0], "hello")
		aa1 = And([Literal('Tel'), Regex(r'[0-9]{4}')])
		self.assertEqual(list(aa1.parseString("Tel 0123")), ["Tel", "0123"])
		self.assertRaises(ParseException, aa1.parseString, "hello")
		aa2 = And([Suppress('Tel'), Regex(r'[0-9]{4}')])
		self.assertEqual(aa2.parseString("Tel 0123")[0], "0123")

	def test_Or(self):
		oo0 = Or(['hello'])
		self.assertEqual(oo0.parseString("hello")[0], "hello")
		oo1 = Or(['hello', 'world', 'what'])
		self.assertEqual(oo1.parseString("hello world")[0], "hello")
		self.assertEqual(oo1.parseString("world hello")[0], "world")

if __name__ == "__main__":
	unittest.main()
