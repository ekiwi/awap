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
	def __init__(self):
		self.endpos = 0
		self.parse_actions = [self._defaultParseAction]

	def getRegexString(self):
		return None

	def setParseAction(self, callback):
		self.parse_actions = [callback]

	def _defaultParseAction(self, source, pos, tockens):
		return tockens

class RawRegex(Element):
	def __init__(self, string, parse_actions=None):
		super().__init__()
		self._compiled_re = None
		self._string = string
		if parse_actions:
			self.parse_actions = parse_actions

	def getRegexString(self):
		return self._string

	def parseString(self, string, pos=0):
		if not self._compiled_re:
			self._compiled_re = re.compile(self.getRegexString())
		m = self._compiled_re.match(string, pos)
		if m:
			self.endpos = m.endpos
			res_list = list(m.groups())
			if len(res_list) != len(self.parse_actions):
				# this is NOT a ParseException, since it should never happen
				raise Exception("Error: number of results ({}) is ".format(len(res_list)) +
					"not equal to the number of parse_actions ({})".format(len(self.parse_actions)))
			results = []
			for (result, parse_action) in zip(res_list, self.parse_actions):
				if result:
					# Since this is a simple regex, the result will always be
					# a simple string, directly from python `re` module.
					# To keep the interface consistent with pyparsing,
					# we wrap that string in a list.
					parsed = parse_action(string, pos, [result])
					# Unpack parsed according to some rules observed with
					# pyparsing:
					if parsed is None:
						results.append(result)
					if isinstance(parsed, list):
						results += parsed
					else:
						results.append(parsed)
			return results
		else:
			raise ParseException("Failed to find `{}` @:\n`{}`".format(self.getRegexString(), string[pos:]))

class Regex(RawRegex):
	def __init__(self, string, suppress=False):
		super().__init__(string)
		self._suppress = suppress
		if suppress:
			self.parse_actions = []

	def getRegexString(self):
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
		super().__init__()
		self._elements = elements
		self._compressed_elements = None
		self._is_simple_regex = None

	@property
	def compressedElements(self):
		if not self._compressed_elements:
			self._compressed_elements = self.compressElements(self._elements)
		return self._compressed_elements

	def compressElements(self, elements):
		raise Exception("Abstract method MultiElement::compressElements must be overwritten.")

	def getRegexString(self):
		elements = self.compressedElements
		if len(elements) == 1:
			return elements[0].getRegexString()
		else:
			return None

class And(MultiElement):
	def __init__(self, elements):
		super().__init__(elements)

	def compressElements(self, elements):
		compressed = []
		re_string = ""
		re_parse_actions = []
		for ee in elements:
			if isinstance(ee, str):
				ee = Regex(ee)
			ee_re = ee.getRegexString()
			if ee_re:
				re_string += ee_re
				re_parse_actions += ee.parse_actions
			else:
				if len(re_string) > 0:
					compressed.append(RawRegex(re_string, re_parse_actions))
					re_string = ""
				compressed.append(ee)
		if len(re_string) > 0:
			compressed.append(RawRegex(re_string, re_parse_actions))
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
		re_parse_actions = []
		for ee in elements:
			if isinstance(ee, str):
				ee = Regex(ee)
			ee_re = ee.getRegexString()
			if ee_re:
				re_strings.append(ee_re)
				re_parse_actions += ee.parse_actions
			else:
				compressed.append(ee)
		if len(re_strings) > 0:
			# build or'd regex string and insert at beginning of the list
			re_string = '|'.join(re_strings)
			compressed.insert(0, RawRegex(re_string, re_parse_actions))
		return compressed

	def parseString(self, string, pos=0):
		elements = self.compressedElements
		res = None
		for ee in elements:
			try:
				return ee.parseString(string, pos)
			except ParseException:
				pass
		if res:
			return res
		raise ParseException("Failed to find Or `` @:\n`{}`".format(string[pos:]))