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

import .aclparser
from .fasterparsing import Regex, ParseException, Or, Literal, ZeroOrMore, Suppress, Forward, OneOrMore, Group

class ObjectFactory(aclparser.ObjectFactory):
	def _terms_to_list_or_dict(self, terms):
		""" creates a dictionary if the terms are (key,value) tuples
			returns an empty list if len(terms) == 0
		"""
		if terms is None or len(terms) < 1:
			return []
		if isinstance(terms[0], tuple):
			return {tt[0]: tt[1] for tt in terms}
		else:
			return [tt for tt in terms]

	def create_ActionExpression(self, agent, term):
		return ('action', {'agent': agent, 'term': term})

	def create_FunctionalTerm(self, name, terms):
		terms = self._terms_to_list_or_dict(terms)
		return ('functionalterm', {'name': name, 'terms': terms})

	def create_AtomicFormula(self, tokens):
		if len(tokens) == 1 and tokens[0] == 'true':
			return ('atomicformula', True)
		elif len(tokens) == 1 and tokens[0] == 'false':
			return ('atomicformula', False)
		elif len(tokens) == 1:
			return ('atomicformula', str(tokens[0]))
		elif tokens[0] == 'result':
			return ('atomicformula', 'result', tokens[1], tokens[2])
		else:
			terms = tokens[1:]
			return ( 'atomicformula', str(tokens[0]), terms)

	def create_Wff(self, is_atomic_formula, value):
		if is_atomic_formula:
			return value
		else:
			return ('done', value)

class FPLexicalDefinitionsParser(aclparser.ACLLexicalDefinitionsParser):
	def __init__(self, obj_factory = ObjectFactory()):
		super().__init__(obj_factory)

		# 1.) FIPA SL allows Word to start with " or +, we don't in order to make
		#     it possible to destinguish Integer and StringLiteral from Word
		self.Word = Regex(r'\s*[^\(\)#0-9- "+\?:][^\(\)\s]*')

		# this is different for FP0
		self.String = Or([self.StringLiteral, self.Word])

		self.ParameterName = Suppress(":") + self.String
		self.VariableIdentifier = Suppress("?") + self.String

class FP0Parser(FPLexicalDefinitionsParser):
	def __init__(self, obj_factory = ObjectFactory()):
		super().__init__(obj_factory)

		self.language = 'fipa-sl0'

		# TODO: support float
		self.NumericalConstant = self.Integer
		self.Constant = Or([self.DateTime, self.NumericalConstant, self.String])

		self.PredicateSymbol = self.String
		self.PropositionSymbol = self.String
		self.FunctionSymbol = self.String

		# forward declaration of Term
		self.Term = Forward()

		self.Sequence = Group(Suppress("(") +
			Suppress("sequence") + ZeroOrMore(self.Term) + Suppress(")"))
		self.Sequence.setParseAction(self.parse_as_List)
		self.Set = Group(Suppress("(") +
			Suppress("set") + ZeroOrMore(self.Term) + Suppress(")"))
		self.Sequence.setParseAction(self.parse_as_List)

		self.Agent = self.Term
		self.ParameterValue = self.Term
		self.Parameter = self.ParameterName + self.ParameterValue
		self.Parameter.setParseAction(self.parse_as_Touple)

		self.FunctionalTerm = Or([
			(Suppress("(") + self.FunctionSymbol + ZeroOrMore(self.Term) + Suppress(")")),
			(Suppress("(") + self.FunctionSymbol + ZeroOrMore(self.Parameter) + Suppress(")"))
		])
		self.FunctionalTerm.setParseAction(self.parse_FunctionalTerm)

		self.ActionExpression = (Suppress("(") +
			Suppress("action") + self.Agent + self.Term + Suppress(")"))
		self.ActionExpression.setParseAction(self.parse_ActionExpression)

		self.Term << Or([self.Constant, self.Set, self.Sequence, self.FunctionalTerm, self.ActionExpression])

		self.ActionOp = Literal("done")
		self.AtomicFormula = Or([
			Literal("true"),
			Literal("false"),
			self.PropositionSymbol,
			(Suppress("(") + Literal("result") + self.Term + self.Term + Suppress(")")),
			(Suppress("(") + self.PredicateSymbol + OneOrMore(self.Term) + Suppress(")"))
		])
		self.AtomicFormula.setParseAction(self.parse_AtomicFormula)
		self.Wff = Or([
			Suppress("(") + self.ActionOp + self.ActionExpression + Suppress(")"),
			self.AtomicFormula,
		])
		self.Wff.setParseAction(self.parse_Wff)
		self.Proposition = self.Wff

		self.ContentExpression = Or([self.ActionExpression, self.Proposition])
		self.Content = Suppress("(") + self.ContentExpression + Suppress(")")

	def parse_content(self, content):
		return self.Content.parseString(content)

	def parse_as_Touple(self, source, location, tokens):
		return (tokens[0], tokens[1])

	def parse_as_List(self, source, location, tokens):
		return tokens

	def parse_ActionExpression(self, source, location, tokens):
		return self.obj_factory.create_ActionExpression(tokens[0], tokens[1])

	def parse_FunctionalTerm(self, source, location, tokens):
		# HACK: resolve ambiguity between ActionExpression and FunctionalTerm
		if tokens[0] == "action" and len(tokens) == 3:
			return self.obj_factory.create_ActionExpression(tokens[1], tokens[2])
		return self.obj_factory.create_FunctionalTerm(tokens[0], tokens[1:])

	def parse_AtomicFormula(self, source, location, tokens):
		return self.obj_factory.create_AtomicFormula(tokens)

	def parse_Wff(self, source, location, tokens):
		is_atomic_formula = tokens[0] != 'done'
		value = tokens[0] if is_atomic_formula else tokens[1]
		return self.obj_factory.create_Wff(is_atomic_formula, value)


class TestFPLexicalDefinitionsParser(unittest.TestCase):
	def setUp(self):
		self.p = FPLexicalDefinitionsParser()

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

class TestFP0Parser(unittest.TestCase):
	def setUp(self):
		self.p = FP0Parser()

	def test_NumericalConstant(self):
		self.assertEqual(self.p.NumericalConstant.parseString('+100')[0], 100)
		self.assertEqual(self.p.NumericalConstant.parseString('-100')[0], -100)

	@unittest.expectedFailure
	def test_NumericalConstant_missing_feature(self):
		# Float(not implemented yet => fails)
		self.assertEqual(self.p.NumericalConstant.parseString('-4.5 E -1')[0], float(-0.45))

	def test_Constant(self):
		self.assertEqual(self.p.Constant.parseString('+100')[0], 100)
		self.assertEqual(self.p.Constant.parseString('-100')[0], -100)
		self.assertEqual(
			self.p.Constant.parseString('20150701T143941567')[0],
			datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000))
		self.assertEqual(self.p.Constant.parseString('SingleWordString')[0], 'SingleWordString')
		self.assertEqual(self.p.Constant.parseString('"String"')[0], 'String')

	def test_Sequence(self):
		self.helper_test_Sequence_Set(self.p.Sequence, 'sequence')

	def test_Set(self):
		self.helper_test_Sequence_Set(self.p.Set, 'set')

	def helper_test_Sequence_Set(self, Parser, name):
		s0 = '({0} 0 1 2 3 4)'.format(name)
		self.assertEqual(Parser.parseString(s0)[0], [0,1,2,3,4])
		s1 = '({0} 0 eins "zwei" 00030303T000000000 -4)'.format(name)
		e1 = [0, 'eins', 'zwei', datetime.datetime(year=3, month=3, day=3), -4]
		self.assertEqual(Parser.parseString(s1)[0], e1)
		s2 = '({0} 0 ({0} 10 11 12) 20 30 40)'.format(name)
		self.assertEqual(Parser.parseString(s2)[0][1], [10, 11, 12])

	def test_Parameter(self):
		self.assertEqual(
			self.p.Parameter.parseString(':test 2')[0], ('test', 2))
		self.assertEqual(
			self.p.Parameter.parseString(':"fancy name" (sequence 0 1 2 3)')[0],
			('fancy name', [0,1,2,3]))

	def test_FunctionalTerm(self):
		# import pdb; pdb.set_trace()
		self.assertEqual(
			self.p.FunctionalTerm.parseString('(empty)')[0],
			('functionalterm', {'name': 'empty', 'terms': []}))
		ft1 = '(test 1 "2" "long and complicated" (set 0 1 2))'
		self.assertEqual(
			self.p.FunctionalTerm.parseString(ft1)[0],
			('functionalterm', {'name': 'test', 'terms': [1, '2', 'long and complicated', [0,1,2]]}))
		self.assertEqual(
			self.p.FunctionalTerm.parseString('(param :name test :value 1)')[0],
			('functionalterm', {'name': 'param', 'terms': {'name': 'test', 'value': 1}}))

	def test_ActionExpression(self):
		self.assertEqual(
			self.p.ActionExpression.parseString('(action agent1 term)')[0],
			('action', {'agent': 'agent1', 'term': 'term'}))
		self.assertEqual(
			self.p.ActionExpression.parseString('(action agent23 (set "a b c" 3))')[0],
			('action', {'agent': 'agent23', 'term': ['a b c', 3]}))

	def test_Term(self):
		# Term can be a Constant
		self.assertEqual(self.p.Term.parseString('-100')[0], -100)
		self.assertEqual(
			self.p.Term.parseString('20150701T143941567')[0],
			datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000))
		self.assertEqual(self.p.Term.parseString('SingleWordString')[0], 'SingleWordString')
		self.assertEqual(self.p.Term.parseString('"String"')[0], 'String')
		# Term can be a Sequence
		self.helper_test_Sequence_Set(self.p.Term, 'sequence')
		# Term can be a Set
		self.helper_test_Sequence_Set(self.p.Term, 'set')
		# Term can be a FunctionalTerm
		self.assertEqual(
			self.p.Term.parseString('(test 1 "2" "long and complicated" (set 0 1 2))')[0],
			('functionalterm', {'name': 'test', 'terms': [1, '2', 'long and complicated', [0,1,2]]}))
		# Term can be a ActionExpression
		# this seems to be ambiguous, thus there is no defined way for our
		# parser to handle this
		self.assertEqual(
			self.p.Term.parseString('(action agent1 term)')[0],
			('action', {'agent': 'agent1', 'term': 'term'}))
		self.assertEqual(
			self.p.Term.parseString('(action agent23 (set "a b c" 3))')[0],
			('action', {'agent': 'agent23', 'term': ['a b c', 3]}))

	def test_AtomicFormula(self):
		self.assertEqual(self.p.AtomicFormula.parseString('true')[0],
			('atomicformula', True))
		self.assertEqual(self.p.AtomicFormula.parseString('false')[0],
			('atomicformula', False))
		self.assertEqual(
			self.p.AtomicFormula.parseString('(result 1 2)')[0],
			('atomicformula', 'result', 1, 2) )
		self.assertEqual(
			self.p.AtomicFormula.parseString('(result 1 (set 3 4 5))')[0],
			('atomicformula', 'result', 1, [3, 4, 5]))
		self.assertEqual(
			self.p.AtomicFormula.parseString(
			'("some string that is not result" 1 (set 3 4 5))')[0],
			('atomicformula', 'some string that is not result', [1, [3, 4, 5]]))

	def test_Wff(self):
		self.assertEqual(
			self.p.Wff.parseString(
			'("some string that is not result" 1 (set 3 4 5))')[0],
			('atomicformula', 'some string that is not result', [1, [3, 4, 5]]))
		self.assertEqual(
			self.p.Wff.parseString(
			'(done (action agent1 test))')[0],
			('done', ('action', {'agent': 'agent1', 'term': 'test'})))

	def test_Content(self):
		c0 = '((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))'
		action = self.p.parse_content(c0)[0]
		self.assertEqual(action[0], 'action')
		agent = action[1]['agent']
		self.assertEqual(agent[1]['name'], 'agent-identifier')
		self.assertEqual(agent[1]['terms']['addresses'][0], 'http://localhost:9000')
		self.assertEqual(agent[1]['terms']['name'], 'test')
		term = action[1]['term']
		self.assertEqual(term[0], 'functionalterm')
		self.assertEqual(term[1]['name'], 'get-description')

		# parsing this takes way too long...
		c1 = '((result (action (agent-identifier :name ams@192.168.122.1:1099/JADE :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)) (get-description)) (sequence (ap-description :name "\\"192.168.122.1:1099/JADE\\"" :ap-services (sequence (ap-service :name fipa.mts.mtp.http.std :type fipa.mts.mtp.http.std :addresses (sequence http://ip2-127.halifax.rwth-aachen.de:7778/acc)))))))'
		result = self.p.parse_content(c1)[0]

if __name__ == "__main__":
	unittest.main()
