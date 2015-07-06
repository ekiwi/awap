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
from pyparsing import Regex, ParseException, Or, Literal, ZeroOrMore, Suppress, Forward, OneOrMore, Group
import aclparser

class FPLexicalDefinitionsParser(aclparser.ACLLexicalDefinitionsParser):
	def __init__(self,):
		super().__init__()

		# 1.) FIPA SL allows Word to start with " or +, we don't in order to make
		#     it possible to destinguish Integer and StringLiteral from Word
		self.Word = Regex(r'\s*[^\(\)#0-9- "+\?:][^\(\)\s]*')

		# this is different for FP0
		self.String = Or([self.StringLiteral, self.Word])

		self.ParameterName = Suppress(":") + self.String
		self.VariableIdentifier = Suppress("?") + self.String

class FP0Parser(FPLexicalDefinitionsParser):
	def __init__(self):
		super().__init__()

		self.language = 'fipa-sl0'

		# TODO: support float
		self.NumericalConstant = self.Integer
		self.Constant = Or([self.NumericalConstant, self.String, self.DateTime])

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

		self.ActionExpression = (Suppress("(") +
			Suppress("action") + self.Agent + self.Term + Suppress(")"))
		self.ActionExpression.setResultsName('action')

		self.Term << Or([self.Constant, self.Set, self.Sequence, self.FunctionalTerm, self.ActionExpression])

		self.ActionOp = Literal("done")
		self.AtomicFormula = Or([
			Literal("true"),
			Literal("false"),
			self.PropositionSymbol,
			(Suppress("(") + Literal("result") + self.Term + self.Term + Suppress(")")),
			(Suppress("(") + self.PredicateSymbol + OneOrMore(self.Term) + Suppress(")"))
		])
		self.Wff = Or([
			self.AtomicFormula,
			Suppress("(") + self.ActionOp + self.ActionExpression + Suppress(")")
		])
		self.Proposition = self.Wff

		self.ContentExpression = Or([self.ActionExpression, self.Proposition])
		self.Content = Suppress("(") + self.ContentExpression + Suppress(")")

	def parse_as_Touple(self, source, location, tokens):
		return (tokens[0], tokens[1])

	def parse_as_List(self, source, location, tokens):
		return tokens.asList()


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
		self.assertEqual(Parser.parseString(s0).asList()[0], [0,1,2,3,4])
		s1 = '({0} 0 eins "zwei" 00030303T000000000 -4)'.format(name)
		e1 = [0, 'eins', 'zwei', datetime.datetime(year=3, month=3, day=3), -4]
		self.assertEqual(Parser.parseString(s1).asList()[0], e1)
		s2 = '({0} 0 ({0} 10 11 12) 20 30 40)'.format(name)
		self.assertEqual(Parser.parseString(s2).asList()[0][1], [10, 11, 12])

	def test_Parameter(self):
		self.assertEqual(
			self.p.Parameter.parseString(':test 2').asList()[0], ('test', 2))
		self.assertEqual(
			self.p.Parameter.parseString(':"fancy name" (sequence 0 1 2 3)').asList()[0],
			('fancy name', [0,1,2,3]))

	@unittest.skip("wip")
	def test_FunctionalTerm(self):
		self.assertEqual(
			self.p.FunctionalTerm.parseString('(empty)').asList(), ['empty'])
		ft1 = '(test 1 "2" "long and complicated" (set 0 1 2))'
		self.assertEqual(
			self.p.FunctionalTerm.parseString(ft1).asList(),
			{'test': [1, '2', 'long and complicated', [0,1,2]]})
		self.assertEqual(
			self.p.FunctionalTerm.parseString('(action agent1 term)').asList(),
			{'action': ['agent1', 'term']})
		self.assertEqual(
			self.p.FunctionalTerm.parseString('(param :name test :value 1)').asList(),
			{'param': {'name': 'test', 'value': 1}})

	@unittest.skip("wip")
	def test_ActionExpression(self):
		self.assertEqual(
			self.p.ActionExpression.parseString('(action agent1 term)').asDict(),
			{'action': ['agent1', 'term']})
		self.assertEqual(
			self.p.ActionExpression.parseString('(action agent23 (set "a b c" 3))').asDict(),
			{'action': ['agent23', ['a b c', 3]]})

	@unittest.skip("wip")
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
			self.p.Term.parseString('(test 1 "2" "long and complicated" (set 0 1 2))').asList(),
			{'test': [1, '2', 'long and complicated', [0,1,2]]})
		# Term can be a ActionExpression
		# this seems to be ambiguous, thus there is no defined way for our
		# parser to handle this
		self.assertEqual(
			self.p.Term.parseString('(action agent1 term)').asList(),
			{'action': ['agent1', 'term']})
		self.assertEqual(
			self.p.Term.parseString('(action agent23 (set "a b c" 3))').asList(),
			{'action': ['agent23', ['a b c', 3]]})

	@unittest.skip("wip")
	def test_AtomicFormula(self):
		self.assertEqual(self.p.AtomicFormula.parseString('true')[0], 'true')
		self.assertEqual(self.p.AtomicFormula.parseString('false')[0], 'false')
		self.assertEqual(
			self.p.AtomicFormula.parseString('(result 1 2)').asList(),
			['result', 1, 2])
		self.assertEqual(
			self.p.AtomicFormula.parseString('(result 1 (set 3 4 5))').asList(),
			['result', 1, [3, 4, 5]])
		self.assertEqual(
			self.p.AtomicFormula.parseString(
			'("some string that is not result" 1 (set 3 4 5))').asList(),
			['some string that is not result', 1, [3, 4, 5]])

	@unittest.skip("wip")
	def test_Wff(self):
		self.assertEqual(
			self.p.Wff.parseString(
			'("some string that is not result" 1 (set 3 4 5))').asList(),
			['some string that is not result', 1, [3, 4, 5]])
		self.assertEqual(
			self.p.Wff.parseString(
			'(done (action agent1 test))').asList(),
			['done', 'action' ,'agent1', 'test'])

	@unittest.skip("wip")
	def test_Content(self):
		c0 = '((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))'
		self.assertEqual(
			self.p.Content.parseString(c0).asList(),
			['agent-identifier', 'name', 'test', 'addresses',
				['http://localhost:9000'], 'get-description'])
		print(self.p.Content.parseString(c0).asXML())


if __name__ == "__main__":
	unittest.main()
