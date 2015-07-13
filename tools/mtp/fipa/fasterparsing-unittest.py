#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# fasterparsing-unittest.py

import unittest, datetime

#from pyparsing import Literal, Suppress, Regex, ParseException, And, Or, CaselessKeyword, ZeroOrMore
from fasterparsing import Literal, Suppress, Regex, ParseException, And, Or, CaselessKeyword, ZeroOrMore

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
		aa3 = And([Literal('Tel'), Regex(r'[0-9]{4}')]).suppress()
		self.assertEqual(len(aa3.parseString("Tel 0123")), 0)
		aa4 = Suppress('Tel') + Regex(r'[0-9]{4}')
		self.assertEqual(aa4.parseString("Tel 0123")[0], "0123")
		aa5 = Suppress('(') + Suppress('Tel') + Regex(r'[0-9]{4}') + Suppress(')')
		self.assertEqual(aa5.parseString("Tel 0123")[0], "0123")

	def parse_Tel(self, message, pos, tokens):
		return {'country': tokens[0], 'area': [1], 'local': [2]}

	def test_And_Nesting(self):
		Tel = (
			Suppress('Tel.:') + Regex(r'(?:[+]{1,2}|(?:00))?[0-9]{1,2}') +
			Regex('[0-9]{3}') + Regex('[0-9]{4}'))
		Tel.setParseAction(self.parse_Tel)
		TelAndName = Tel + Suppress('Name:') + Regex('[a-zA-Z]+')
		res = TelAndName.parseString('Tel.: 49 023 1567 Name: Test')
		self.assertEqual(res[0]['local'], '1567')
		self.assertEqual(res[0]['country'], '49')
		self.assertEqual(res[0]['area'], '023')
		self.assertEqual(res[1], 'Test')

	def test_Or(self):
		oo0 = Or(['hello'])
		self.assertEqual(oo0.parseString("hello")[0], "hello")
		oo1 = Or(['hello', 'world', 'what'])
		self.assertEqual(oo1.parseString("hello world")[0], "hello")
		self.assertEqual(oo1.parseString("world hello")[0], "world")
		oo2 = Or(['hello', 'world', 'what']).suppress()
		self.assertEqual(len(oo2.parseString("world hello")), 0)

	def test_ZeroOrMore(self):
		zom0 = ZeroOrMore(Regex(r'[0-9]+'))
		self.assertEqual(len(zom0.parseString("hello")), 0)
		self.assertEqual(len(zom0.parseString("0")), 1)
		self.assertEqual(len(zom0.parseString("0123")), 1)
		self.assertEqual(len(zom0.parseString("0 1 2 3")), 4)
		self.assertEqual(list(zom0.parseString("0 1 2 3 test")), ['0', '1', '2', '3'])

if __name__ == "__main__":
	unittest.main()
