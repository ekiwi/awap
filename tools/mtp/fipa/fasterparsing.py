#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# fasterparsing.py
# tries to be a faster implementation of the subset of pyparsing that is
# used in the awap bridge application

import re, operator


# Optional, ZeroOrMore, CaselessKeyword

class ParseException(Exception):
	pass

class Element(object):
	def __init__(self, suppress=False):
		self.endpos = 0
		self._parse_actions = [self._defaultParseAction]
		self._suppress = suppress

	def getRegexString(self):
		return None

	def setParseAction(self, callback):
		self._parse_actions = [callback]

	@property
	def parse_actions(self):
		return self._parse_actions

	def _defaultParseAction(self, source, pos, tockens):
		return tockens

	def suppress(self):
		self._suppress = True
		return self

	def __add__(self, other):
		return And([self, other])

	def __repr__(self):
		return str(self)

class RawRegex(Element):
	def __init__(self, string, parse_actions=None, suppress=False):
		super().__init__(suppress)
		self._compiled_re = None
		self._string = string
		if parse_actions is not None:
			self._parse_actions = parse_actions

	def getRegexString(self):
		return self._string

	def parseString(self, string, pos=0):
		if not self._compiled_re:
			self._compiled_re = re.compile(self.getRegexString())
		m = self._compiled_re.match(string, pos)
		if m:
			self.endpos = m.end(0)
			res_list = list(m.groups())
			if len(res_list) != len(self._parse_actions):
				# this is NOT a ParseException, since it should never happen
				raise Exception("Error: number of results ({}) is ".format(len(res_list)) +
					"not equal to the number of parse_actions ({})".format(len(self._parse_actions)) +
					'\nin: `{}`'.format(self) +
					'\nresults:      {}'.format(res_list) +
					'\nparse_actions: {}'.format(self._parse_actions) +
					'\n@ pos:{} => "{}"'.format(pos, string[pos:]) +
					'\nm: {}'.format(m))
			results = []
			for (result, parse_action) in zip(res_list, self._parse_actions):
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

	def __str__(self):
		return '{}(\'{}\')'.format(self.__class__.__name__, str(self._string))

class Regex(RawRegex):
	def __init__(self, string, suppress=False):
		super().__init__(string, None, suppress)
		if self._suppress:
			self._parse_actions = []

	def getRegexString(self):
		if self._suppress:
			templ = '\s*(?:{})'
		else:
			templ = '\s*({})'
		return templ.format(self._string)

class Literal(Regex):
	def __init__(self, string, suppress=False):
		super().__init__(re.escape(string), suppress)

class CaselessKeyword(Regex):
	def __init__(self, string, suppress=False):
		# TODO: this does not work for all possible inputs
		string = re.escape(string)
		regex = ''.join(['[{}{}]'.format(c.upper(), c.lower()) for c in string])
		super().__init__(regex, suppress)
		self._parse_actions = [self.returnKeyword]
		self._keyword = string

	def returnKeyword(self, source, pos, tockens):
		return self._keyword

class Suppress(Literal):
	def __init__(self, string):
		super().__init__(string, suppress=True)

class MultiElement(Element):
	def __init__(self, elements, suppress=False):
		super().__init__(suppress)
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

	def _can_simplify_to_regex(self):
		# only if we can compress to one element and if this MultiElement,
		# does not have a custom parse_action, can we simplify this
		# into a simple regex
		# print(self._elements)
		# print(len(elements) == 1, self._parse_actions[0] == self._defaultParseAction)
		return len(self.compressedElements) == 1 and self._parse_actions[0] == self._defaultParseAction

	@property
	def parse_actions(self):
		if self._can_simplify_to_regex():
			return self.compressedElements[0].parse_actions
		else:
			return self._parse_actions

	def getRegexString(self):
		if self._can_simplify_to_regex():
			return self.compressedElements[0].getRegexString()
		else:
			return None

	def _parseResults(self, string, pos, results):
		""" Convenience function that runs results through the parse_action
			and tries to mimic pyparsing behavior.
		"""
		parsed = self._parse_actions[0](string, pos, results)
		# Unpack parsed according to some rules observed with
		# pyparsing:
		if parsed is None:
			return results
		if isinstance(parsed, list):
			return parsed
		else:
			return [parsed]

	def __str__(self):
		return '{}({})'.format(self.__class__.__name__, str(self._elements))

class And(MultiElement):
	def __init__(self, elements, suppress=False):
		super().__init__(elements, suppress)

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
					re_parse_actions = []
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
		if self._suppress:
			return []
		else:
			return self._parseResults(string, pos, results)

	def __add__(self, other):
		# check if there are any specific settings
		if self._parse_actions[0] == self._defaultParseAction and not self._suppress:
			self._compressed_elements = None
			self._elements.append(other)
			return self
		else:
			return And([self, other])

class Or(MultiElement):
	def __init__(self, elements, suppress=False):
		super().__init__(elements, suppress)

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
			re_string = '(?:{})'.format('|'.join(re_strings))
			compressed.insert(0, RawRegex(re_string, re_parse_actions))
		return compressed

	def parseString(self, string, pos=0):
		elements = self.compressedElements
		for ee in elements:
			try:
				res = ee.parseString(string, pos)
				self.endpos = ee.endpos
				if self._suppress:
					return []
				else:
					return self._parseResults(string, pos, res)
			except ParseException:
				pass
		raise ParseException("Failed to find Or `` @:\n`{}`".format(string[pos:]))

class WrapperElement(Element):
	def __init__(self, element, suppress=False):
		super().__init__(suppress)
		self._element = element

	def __str__(self):
		return '{}({})'.format(self.__class__.__name__, str(self._element))

class ZeroOrMore(WrapperElement):
	def __init__(self, element, suppress=False):
		super().__init__(element, suppress)

	def parseString(self, string, pos=0):
		results = []
		while True:
			try:
				results += self._element.parseString(string, pos)
				pos = self._element.endpos
			except ParseException:
				break
		self.endpos = pos
		return results

class OneOrMore(WrapperElement):
	def __init__(self, element, suppress=False):
		super().__init__(element, suppress)

	def parseString(self, string, pos=0):
		results = self._element.parseString(string, pos)
		pos = self._element.endpos
		while True:
			try:
				results += self._element.parseString(string, pos)
				pos = self._element.endpos
			except ParseException:
				break
		self.endpos = pos
		return results

class Group(WrapperElement):
	def __init__(self, element, suppress=False):
		super().__init__(element, suppress)
		self._parse_actions = [self._parse_to_list]

	def parseString(self, string, pos=0):
		res = [self._element.parseString(string, pos)]
		self.endpos = self._element.endpos
		return res

	def _parse_to_list(self, source, pos, tockens):
		return [tockens]

class Forward(WrapperElement):
	def __init__(self, suppress=False):
		super().__init__(None, suppress)

	def parseString(self, string, pos=0):
		if self._element is None:
			return None
		else:
			res = self._element.parseString(string, pos)
			self.endpos = self._element.endpos
			return res

	def __lshift__(self, other):
		self._element = other

	def __str__(self):
		return 'Forward'
