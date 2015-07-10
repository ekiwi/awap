#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import datetime
from pyparsing import Regex, ParseException, Or, Literal, Optional, ZeroOrMore, Suppress

class ObjectFactory(object):
	def create_int(self, value):
		return int(value)
	def create_AgentIdentifier(self, name, addresses):
		return {'name': name, 'addresses': list(addresses) }

class ACLLexicalDefinitionsParser(object):
	def __init__(self, obj_factory = ObjectFactory()):
		self.obj_factory = obj_factory

		self.DateTime = Regex(r'([\+-])?\d{8}T\d{9}([a-zA-Z])?')
		self.DateTime.setParseAction(self.parse_DateTime)

		self.StringLiteral = Regex(r'"([^"\\]|(\\.))+"')
		self.StringLiteral.setParseAction(self.parse_StringLiteral)

		# 1.) FIPA ACL allows Word to start with " or +, we don't in order to make
		#     it possible to destinguish Integer and StringLiteral from Word
		self.Word = Regex(r'\s*[^\(\)#0-9-@ "+][^\(\)\s]*')

		self.Integer = Regex(r'[\+-]?[0-9]+')
		self.Integer.setParseAction(self.parse_Integer)

		self.Number = self.Integer

		self.String = self.StringLiteral

		# inspired by: https://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
		# TODO: this is not correct, as any URL, not only http urls should be accepted...
		self.URL = Regex(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-&*-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


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

	def parse_StringLiteral(self, source, location, tokens):
		tok = tokens[0][1:-1]
		tok = tok.replace('\\"', '"')
		return tok

	def parse_Integer(self, source, location, tokens):
		return self.obj_factory.create_int(tokens[0])

class ACLParser(ACLLexicalDefinitionsParser):
	def __init__(self, obj_factory = ObjectFactory()):
		super().__init__(obj_factory)

		self.URLSequence = Suppress("(") + Suppress("sequence") + ZeroOrMore(self.URL) + Suppress(")")

		self.AgentIdentifier = (
			Suppress("(") + Suppress("agent-identifier") + Suppress(":name") +
			self.Word.setResultsName('name') + Optional(Suppress(":addresses") +
			self.URLSequence).setResultsName('addresses') + Suppress(")"))
		self.AgentIdentifier.setParseAction(self.parse_AgentIdentifier)

		self.AgentIdentifierSet = (
			Suppress("(") + Suppress("set") + ZeroOrMore(self.AgentIdentifier) + Suppress(")"))

		self.Expression = Or([self.Word, self.String, self.Number, self.DateTime])

		self.Performative = ["ACCEPT_PROPOSAL", "AGREE", "CANCEL", "CFP", "CONFIRM"
			"DISCONFIRM", "FAILURE", "INFORM", "INFORM_IF", "INFORM_REF",
			"NOT_UNDERSTOOD", "PROPOSE", "QUERY_IF", "QUERY_REF", "REFUSE",
			"REJECT_PROPOSAL", "REQUEST", "REQUEST_WHEN", "REQUEST_WHENEVER",
			"SUBSCRIBE", "PROXY", "PROPAGATE"]


		self.MessageType = Or(self.Performative).setResultsName('performative')

		self.MessageParameterNames = ['sender', 'receiver', 'content',
			'reply-with', 'reply-by', 'in-reply-to', 'reply-to', 'language',
			'encoding', 'ontology', 'protocol', 'conversation-id']

		self.MessageParameter = Or([
			(Suppress(":sender") + self.AgentIdentifier).setResultsName('sender'),
			(Suppress(":receiver") + self.AgentIdentifierSet).setResultsName('receiver'),
			(Suppress(":content") + self.String).setResultsName('content'),
			(Suppress(":reply-with") + self.Expression).setResultsName('reply-with'),
			(Suppress(":reply-by") + self.DateTime).setResultsName('reply-by'),
			(Suppress(":in-reply-to") + self.Expression).setResultsName('in-reply-to'),
			(Suppress(":reply-to") + self.AgentIdentifierSet).setResultsName('reply-to'),
			(Suppress(":language") + self.Expression).setResultsName('language'),
			(Suppress(":encoding") + self.Expression).setResultsName('encoding'),
			(Suppress(":ontology") + self.Expression).setResultsName('ontology'),
			(Suppress(":protocol") + self.Word).setResultsName('protocol'),
			(Suppress(":conversation-id") + self.Expression).setResultsName('conversation-id')
			])

		self.Message = Suppress("(") + self.MessageType + ZeroOrMore(self.MessageParameter) + Suppress(")")

	def parse_message(self, msg):
		return self.Message.parseString(msg)

	def parse_AgentIdentifier(self, source, location, tokens):
		name = tokens['name']
		addresses = tokens['addresses']
		return self.obj_factory.create_AgentIdentifier(name, addresses)


class TestACLLexicalDefinitionsParser(unittest.TestCase):
	def setUp(self):
		self.p = ACLLexicalDefinitionsParser(ObjectFactory())

	def test_DateTime(self):
		ts = datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000)
		self.assertEqual(self.p.DateTime.parseString("20150701T143941567")[0], ts)
		self.assertEqual(self.p.DateTime.parseString("+20150701T143941567")[0], ts)
		self.assertEqual(self.p.DateTime.parseString("-20150701T143941567z")[0], ts)
		self.assertRaises(ParseException, self.p.DateTime.parseString, "20150701Z143941567")
		self.assertRaises(ParseException, self.p.DateTime.parseString, "d20150701T143941567")
		self.assertRaises(ParseException, self.p.DateTime.parseString, "20150d01T143941567")
		self.assertRaises(ParseException, self.p.DateTime.parseString, "20150701T14394156")

	def test_StringLiteral(self):
		self.assertEqual(self.p.StringLiteral.parseString('"String"')[0], 'String')
		self.assertEqual(self.p.StringLiteral.parseString('"str\\"ing"')[0], 'str"ing')
		self.assertEqual(self.p.StringLiteral.parseString('"String"not part of this String')[0], 'String')
		self.assertRaises(ParseException, self.p.StringLiteral.parseString, 'not a String literal')

	def test_Word(self):
		self.assertEqual(self.p.Word.parseString('Word')[0], 'Word')
		self.assertEqual(self.p.Word.parseString('WoRd')[0], 'WoRd')
		self.assertEqual(self.p.Word.parseString('w#ord')[0], 'w#ord')
		self.assertEqual(self.p.Word.parseString('w0rd')[0], 'w0rd')
		self.assertEqual(self.p.Word.parseString('w-r+d')[0], 'w-r+d')
		self.assertEqual(self.p.Word.parseString('rma@192.168.122.1:1099/JADE')[0], 'rma@192.168.122.1:1099/JADE')
		self.assertEqual(self.p.Word.parseString('fipa-request\n')[0], 'fipa-request')
		self.assertRaises(ParseException, self.p.Word.parseString, '#notaWord')

	def test_Integer(self):
		self.assertEqual(self.p.Integer.parseString('+100')[0], 100)
		self.assertEqual(self.p.Integer.parseString('-100')[0], -100)

	def test_String(self):
		# StringLiteral
		self.assertEqual(self.p.String.parseString('"String"')[0], 'String')
		self.assertEqual(self.p.String.parseString('"String1" "String2"')[0], 'String1')

	@unittest.expectedFailure
	def test_String_missing_feature(self):
		# ByteLengthEncodedString (not implemented yet => fails)
		self.assertEqual(self.p.String.parseString('#6"String')[0], 'String')

	def test_URL(self):
		self.assertEqual(self.p.URL.parseString('http://test/')[0], 'http://test/')
		self.assertEqual(self.p.URL.parseString('http://1')[0], 'http://1')
		self.assertEqual(self.p.URL.parseString(
			'http://ip2-127.halifax.rwth-aachen.de:7778/acc')[0],
			'http://ip2-127.halifax.rwth-aachen.de:7778/acc')
		self.assertEqual(self.p.URL.parseString(
			'http://130-000.eduroam.rwth-aachen.de:7778/acc')[0],
			'http://130-000.eduroam.rwth-aachen.de:7778/acc')
		# even if this might rule out some legitimate urls, it is important,
		# that the closing bracket is NOT matched
		# this behavior is needed in order for the URLSequence to work
		self.assertEqual(self.p.URL.parseString('http://1)')[0], 'http://1')

class TestACLStringParser(unittest.TestCase):
	def setUp(self):
		self.p = ACLParser(ObjectFactory())

	def test_Expression(self):
		ts = datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000)
		self.assertEqual(self.p.Expression.parseString("20150701T143941567")[0], ts)
		self.assertEqual(self.p.Expression.parseString('"String"')[0], 'String')
		self.assertEqual(self.p.Expression.parseString('w#ord')[0], 'w#ord')
		self.assertEqual(self.p.Expression.parseString('+100')[0], 100)

	def test_URLSequence(self):
		s0 = "(sequence http://1 http://2 http://3)"
		s1 = "( sequence http://1 http://2 http://3 )"
		s2 = "(  sequence  http://1   http://2 http://3)"
		s3 = "(  sequence  http://1   http://2)"
		s4 = "(sequence http://130-000.eduroam.rwth-aachen.de:7778/acc )"
		res = ['http://1', 'http://2', 'http://3']
		self.assertEqual(list(self.p.URLSequence.parseString(s0)), res)
		self.assertEqual(list(self.p.URLSequence.parseString(s1)), res)
		self.assertEqual(list(self.p.URLSequence.parseString(s2)), res)
		self.assertEqual(list(self.p.URLSequence.parseString(s3)), ['http://1', 'http://2'])
		self.assertEqual(list(self.p.URLSequence.parseString(s4)), ['http://130-000.eduroam.rwth-aachen.de:7778/acc'])

	def test_AgentIdentifier(self):
		a0 = "( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ) )"
		a1 = "( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )"
		res0 = self.p.AgentIdentifier.parseString(a0)[0]
		self.assertEqual(res0['name'], 'rma@192.168.122.1:1099/JADE')
		self.assertEqual(list(res0['addresses']), ['http://130-000.eduroam.rwth-aachen.de:7778/acc'])
		self.assertEqual(list(self.p.AgentIdentifier.parseString(a1)[0]['addresses']), ['http://1', 'http://2'])

	def test_AgentIdentifierSet(self):
		s0 = "(set ( agent-identifier :name test  :addresses (sequence http://1 )) )"
		s1 = "(set ( agent-identifier :name test  :addresses (sequence http://1 ) ) )"
		s2 = "(  set ( agent-identifier :name test  :addresses ( sequence http://1 ) ) )"
		expect0 = {'name': 'test', 'addresses': ['http://1']}
		s3 = "(set ( agent-identifier :name t1  :addresses (sequence http://1 )) ( agent-identifier :name t2  :addresses (sequence http://2 )) )"
		expect3 = [{'name': 't1', 'addresses': ['http://1']}, {'name': 't2', 'addresses': ['http://2']}]
		self.assertEqual(self.p.AgentIdentifierSet.parseString(s0)[0], expect0)
		self.assertEqual(self.p.AgentIdentifierSet.parseString(s1)[0], expect0)
		self.assertEqual(self.p.AgentIdentifierSet.parseString(s2)[0], expect0)
		self.assertEqual(list(self.p.AgentIdentifierSet.parseString(s3)), expect3)

	def test_MessageParameter(self):
		self.assertRaises(ParseException, self.p.MessageParameter.parseString, ":sender wrong")
		self.assertRaises(ParseException, self.p.MessageParameter.parseString, ":sender 100")
		self.assertRaises(ParseException, self.p.MessageParameter.parseString, ":invalid ( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )")

		inp = ":sender ( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )"
		out = self.p.MessageParameter.parseString(inp)

		self.assertTrue('sender' in out)
		self.assertEqual(out['sender'][0], {'name': 'test', 'addresses': ['http://1', 'http://2']})

		out = self.p.MessageParameter.parseString(":reply-by 20150701T143941567")
		self.assertTrue('reply-by' in out)
		self.assertEqual(out['reply-by'][0], datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000))

	def test_Message(self):
		msg = ('\n\n(REQUEST\n' +
			' :sender  ( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ))\n' +
			' :receiver  (set ( agent-identifier :name test  :addresses (sequence http://localhost:9000 )) )\n' +
			' :content  "((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))" \n' +
			' :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request\n' +
			' :conversation-id  C1438784720_1435754381566 )\n\n\n')
		out = self.p.parse_message(msg)

		self.assertEqual(out['performative'], 'REQUEST')
		self.assertEqual(out['sender'][0]['name'], 'rma@192.168.122.1:1099/JADE')
		self.assertEqual(out['sender'][0]['addresses'], ['http://130-000.eduroam.rwth-aachen.de:7778/acc'])
		self.assertEqual(out['receiver'][0]['name'], 'test')
		self.assertEqual(out['receiver'][0]['addresses'], ['http://localhost:9000'])
		self.assertEqual(out['content'][0], '((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))')
		self.assertEqual(out['language'][0], 'fipa-sl0')
		self.assertEqual(out['ontology'][0], 'FIPA-Agent-Management')
		self.assertEqual(out['protocol'][0], 'fipa-request')
		self.assertEqual(out['conversation-id'][0], 'C1438784720_1435754381566')



if __name__ == "__main__":
	unittest.main()
