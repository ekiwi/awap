#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module describes a parser for the FIPA SL0 Conent Language.
The number one goal is to be able to communicate with the AMS
on a JADE system. Thus the parser is neither complete, nor fully correct.

The FIPA SL Content Language Specification can be found here:
http://www.fipa.org/specs/fipa00008/SC00008I.html
"""

import unittest
import datetime
from pyparsing import Regex, ParseException, Or, Literal, Optional, ZeroOrMore, Suppress

from aclparser import TestObjectFactory, ACLLexicalDefinitionsParser

class FPLexicalDefinitionsParser(ACLLexicalDefinitionsParser):
	def __init__(self, obj_factory = TestObjectFactory()):
		super().__init__(obj_factory)

		# 1.) FIPA SL allows Word to start with " or +, we don't in order to make
		#     it possible to destinguish Integer and StringLiteral from Word
		self.Word = Regex(r'\s*[^\(\)#0-9- "+\?:][^\(\)\s]*')

		# this is different for FP0
		self.String = Or([self.StringLiteral, self.Word])

		self.ParameterName = Suppress(":") + self.String
		self.VariableIdentifier = Suppress("?") + self.String


class TestFPLexicalDefinitionsParser(unittest.TestCase):
	def setUp(self):
		self.p = FPLexicalDefinitionsParser(TestObjectFactory())

	def test_String(self):
		self.assertEqual(self.p.String.parseString('SingleWordString')[0], 'SingleWordString')
		# a leading '@' for a Word is allowed in SL, but not in ACL
		self.assertEqual(self.p.String.parseString('@SingleWordString')[0], '@SingleWordString')
		self.assertRaises(ParseException, self.p.String.parseString, '#notaWord')
		# a leading ':' or '?' is not allowed in SL, but allowed in ACL
		self.assertRaises(ParseException, self.p.String.parseString, ':ParameterName')
		self.assertRaises(ParseException, self.p.String.parseString, '?VariableIdentifier')
		self.assertEqual(self.p.String.parseString('"String"')[0], 'String')

	@unittest.expectedFailure
	def test_String_missing_feature(self):
		# ByteLengthEncodedString (not implemented yet => fails)
		self.assertEqual(self.p.String.parseString('#6"String')[0], 'String')

	def testParameterName(self):
		self.assertEqual(self.p.ParameterName.parseString(':ParameterName')[0], 'ParameterName')
		self.assertEqual(self.p.ParameterName.parseString(':@ParameterName')[0], '@ParameterName')
		self.assertEqual(self.p.ParameterName.parseString(
			':"You can have really long \\" parameter names, lol."')[0],
			'You can have really long " parameter names, lol.')

	def testVariableIdentifier(self):
		self.assertEqual(self.p.VariableIdentifier.parseString('?VariableIdentifier')[0], 'VariableIdentifier')
		self.assertEqual(self.p.VariableIdentifier.parseString('?@VariableIdentifier')[0], '@VariableIdentifier')
		self.assertEqual(self.p.VariableIdentifier.parseString(
			'?"You can have really long \\" variable identifiers, lol."')[0],
			'You can have really long " variable identifiers, lol.')


if __name__ == "__main__":
	unittest.main()
