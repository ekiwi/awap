#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# fasterparsing.py
# tries to be a faster implementation of the subset of pyparsing that is
# used in the awap bridge application

import unittest
import re, operator


# Optional, ZeroOrMore, CaselessKeyword

class ParseException(Exception):
	pass

class Element(object):
	def __init__(self, isSimpleRegex):
		# is true if this element can be represented by a regex
		self.endpos = 0
		if isSimpleRegex:
			self.isSimpleRegex = isSimpleRegex

	def getRegexString(self):
		if self.isSimpleRegex:
			return self._getRegexString()
		else:
			raise Exception("Element is not a simple regex, thus there is no regex string to return.")

	def _getRegexString(self):
		raise Exception("Abstract method Element::_getRegexString must be overwritten.")

class RawRegex(Element):
	def __init__(self, string):
		super().__init__(True)
		self._compiled_re = None
		self._string = string

	def _getRegexString(self):
		return self._string

	def parseString(self, string, pos=0):
		if not self._compiled_re:
			self._compiled_re = re.compile(self.getRegexString())
		m = self._compiled_re.match(string, pos)
		if m:
			self.endpos = m.endpos
			res_list = list(m.groups())
			return [res for res in res_list if res]
		else:
			raise ParseException("Failed to find `{}` @:\n`{}`".format(self.getRegexString(), string[pos:]))

class Regex(RawRegex):
	def __init__(self, string, suppress=False):
		super().__init__(string)
		self._suppress = suppress

	def _getRegexString(self):
		if self._suppress:
			templ = '\s*(?:{})'
		else:
			templ = '\s*({})'
		return templ.format(self._string)

class Literal(Regex):
	def __init__(self, string, suppress=False):
		super().__init__(string, suppress)

class Suppress(Regex):
	def __init__(self, string):
		super().__init__(string, suppress=True)

class MultiElement(Element):
	def __init__(self, elements):
		super().__init__(None)
		self._elements = elements
		self._compressed_elements = None
		self._is_simple_regex = None

	@property
	def isSimpleRegex(self):
		if not self._is_simple_regex:
			self._is_simple_regex = reduce(operator.__and__, [ee.isSimpleRedex for ee in self._elements])
		return self._is_simple_regex

	@property
	def compressedElements(self):
		if not self._compressed_elements:
			self._compressed_elements = self.compressElements(self._elements)
		return self._compressed_elements

	def compressElements(self, elements):
		raise Exception("Abstract method MultiElement::compressElements must be overwritten.")

	def _getRegexString(self):
		return self.compressedElements[0].getRegexString()

class And(MultiElement):
	def __init__(self, elements):
		super().__init__(elements)

	def compressElements(self, elements):
		compressed = []
		re_string = ""
		for ee in elements:
			if isinstance(ee, str):
				re_string += '\s*({})'.format(ee)
			elif ee.isSimpleRegex:
				re_string += ee.getRegexString()
			else:
				if len(re_string) > 0:
					compressed.append(RawRegex(re_string))
					re_string = ""
				compressed.append(ee)
		if len(re_string) > 0:
			compressed.append(RawRegex(re_string))
		return compressed

	def parseString(self, string, pos=0):
		elements = self.compressedElements
		results = []
		for ee in elements:
			res = ee.parseString(string, pos)
			pos = ee.endpos
			if isinstance(res, list):
				results += res
			else:
				results.append(res)
		self.endpos = pos
		return results

class Or(MultiElement):
	def __init__(self, elements):
		super().__init__(elements)

	def compressElements(self, elements):
		compressed = []
		re_strings = []
		for ee in elements:
			if isinstance(ee, str):
				re_strings.append('\s*({})'.format(ee))
			elif ee.isSimpleRegex:
				re_strings.append(ee.getRegexString())
			else:
				compressed.append(ee)
		if len(re_strings) > 0:
			# build or'd regex string and insert at beginning of the list
			re_string = '|'.join(re_strings)
			compressed.insert(0, RawRegex(re_string))
		return compressed

	def parseString(self, string, pos=0):
		elements = self.compressedElements
		res = None
		for ee in elements:
			try:
				return ee.parseString(string, pos)
			except ParserException:
				pass
		if res:
			return res
		raise ParseException("Failed to find Or `` @:\n`{}`".format(string[pos:]))
