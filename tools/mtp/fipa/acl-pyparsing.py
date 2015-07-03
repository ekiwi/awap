#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import datetime
from pyparsing import Regex, ParseException, Or, Literal, Optional, ZeroOrMore, Suppress

class TestObjectFactory(object):
	def create_int(self, value):
		return int(value)
	def create_AgentIdentifier(self, name, addresses):
		return {'name': name, 'addresses': list(addresses) }

obj_factory = TestObjectFactory()

def parse_DateTime(source, location, tokens):
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

def parse_StringLiteral(source, location, tokens):
	tok = tokens[0][1:-1]
	tok = tok.replace('\\"', '"')
	return tok

def parse_Integer(source, location, tokens):
	return obj_factory.create_int(tokens[0])

def parse_AgentIdentifier(source, location, tokens):
	name = tokens['name']
	addresses = tokens['addresses']
	return obj_factory.create_AgentIdentifier(name, addresses)

DateTime = Regex(r'([\+-])?\d{8}T\d{9}([a-zA-Z])?')
DateTime.setParseAction(parse_DateTime)

StringLiteral = Regex(r'"(([^"])|(\"))+"')
StringLiteral.setParseAction(parse_StringLiteral)

# 1.) FIPA ACL allows Word to start with " or +, we don't in order to make
#     it possible to destinguish Integer and StringLiteral from Word
Word = Regex(r'\s*[^\(\)#0-9-@ "+][^\(\)\s]*')

Integer = Regex(r'[\+-]?[0-9]+')
Integer.setParseAction(parse_Integer)

Number = Integer

String = StringLiteral

# inspired by: https://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
# TODO: this is not correct, as any URL, not only http urls should be accepted...
URL = Regex(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-&*-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

URLSequence = Suppress("(") + Suppress("sequence") + ZeroOrMore(URL) + Suppress(")")

AgentIdentifier = (
	Suppress("(") + Suppress("agent-identifier") + Suppress(":name") +
	Word.setResultsName('name') + Optional(Suppress(":addresses") +
	URLSequence).setResultsName('addresses') + Suppress(")"))
AgentIdentifier.setParseAction(parse_AgentIdentifier)

AgentIdentifierSet = (
	Suppress("(") + Suppress("set") + ZeroOrMore(AgentIdentifier) + Suppress(")"))

Expression = Or([Word, String, Number, DateTime])

Performative = ["ACCEPT_PROPOSAL", "AGREE", "CANCEL", "CFP", "CONFIRM"
	"DISCONFIRM", "FAILURE", "INFORM", "INFORM_IF", "INFORM_REF",
	"NOT_UNDERSTOOD", "PROPOSE", "QUERY_IF", "QUERY_REF", "REFUSE",
	"REJECT_PROPOSAL", "REQUEST", "REQUEST_WHEN", "REQUEST_WHENEVER",
	"SUBSCRIBE", "PROXY", "PROPAGATE"]


MessageType = Or(Performative).setResultsName('performative')

MessageParameter = Or([
	(Suppress(":sender") + AgentIdentifier).setResultsName('sender'),
	(Suppress(":receiver") + AgentIdentifierSet).setResultsName('receiver'),
	(Suppress(":content") + String).setResultsName('content'),
	(Suppress(":reply-with") + Expression).setResultsName('reply-with'),
	(Suppress(":reply-by") + DateTime).setResultsName('reply-by'),
	(Suppress(":in-reply-to") + Expression).setResultsName('in-reply-to'),
	(Suppress(":reply-to") + AgentIdentifierSet).setResultsName('reply-to'),
	(Suppress(":language") + Expression).setResultsName('language'),
	(Suppress(":encoding") + Expression).setResultsName('encoding'),
	(Suppress(":ontology") + Expression).setResultsName('ontology'),
	(Suppress(":protocol") + Word).setResultsName('protocol'),
	(Suppress(":conversation-id") + Expression).setResultsName('conversation-id')
	])

Message = Suppress("(") + MessageType + ZeroOrMore(MessageParameter) + Suppress(")")

class TestACLStringParser(unittest.TestCase):

	def test_DateTime(self):
		ts = datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000)
		self.assertEqual(DateTime.parseString("20150701T143941567")[0], ts)
		self.assertEqual(DateTime.parseString("+20150701T143941567")[0], ts)
		self.assertEqual(DateTime.parseString("-20150701T143941567z")[0], ts)
		self.assertRaises(ParseException, DateTime.parseString, "20150701Z143941567")
		self.assertRaises(ParseException, DateTime.parseString, "d20150701T143941567")
		self.assertRaises(ParseException, DateTime.parseString, "20150d01T143941567")
		self.assertRaises(ParseException, DateTime.parseString, "20150701T14394156")

	def test_StringLiteral(self):
		self.assertEqual(StringLiteral.parseString('"String"')[0], 'String')
		self.assertEqual(StringLiteral.parseString('"str\\"ing"')[0], 'str"ing')
		self.assertEqual(StringLiteral.parseString('"String"not part of this String')[0], 'String')
		self.assertRaises(ParseException, StringLiteral.parseString, 'not a String literal')

	def test_Word(self):
		self.assertEqual(Word.parseString('Word')[0], 'Word')
		self.assertEqual(Word.parseString('WoRd')[0], 'WoRd')
		self.assertEqual(Word.parseString('w#ord')[0], 'w#ord')
		self.assertEqual(Word.parseString('w0rd')[0], 'w0rd')
		self.assertEqual(Word.parseString('w-r+d')[0], 'w-r+d')
		self.assertEqual(Word.parseString('rma@192.168.122.1:1099/JADE')[0], 'rma@192.168.122.1:1099/JADE')
		self.assertEqual(Word.parseString('fipa-request\n')[0], 'fipa-request')
		self.assertRaises(ParseException, Word.parseString, '#notaWord')

	def test_Integer(self):
		self.assertEqual(Integer.parseString('+100')[0], 100)
		self.assertEqual(Integer.parseString('-100')[0], -100)

	def test_String(self):
		# StringLiteral
		self.assertEqual(String.parseString('"String"')[0], 'String')

	@unittest.expectedFailure
	def test_String_missing_feature(self):
		# ByteLengthEncodedString (not implemented yet => fails)
		self.assertEqual(String.parseString('#6"String')[0], 'String')

	def test_Expression(self):
		ts = datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000)
		self.assertEqual(Expression.parseString("20150701T143941567")[0], ts)
		self.assertEqual(Expression.parseString('"String"')[0], 'String')
		self.assertEqual(Expression.parseString('w#ord')[0], 'w#ord')
		self.assertEqual(Expression.parseString('+100')[0], 100)

	def test_URL(self):
		self.assertEqual(URL.parseString('http://test/')[0], 'http://test/')
		self.assertEqual(URL.parseString('http://1')[0], 'http://1')
		self.assertEqual(URL.parseString(
			'http://ip2-127.halifax.rwth-aachen.de:7778/acc')[0],
			'http://ip2-127.halifax.rwth-aachen.de:7778/acc')
		self.assertEqual(URL.parseString(
			'http://130-000.eduroam.rwth-aachen.de:7778/acc')[0],
			'http://130-000.eduroam.rwth-aachen.de:7778/acc')
		# even if this might rule out some legitimate urls, it is important,
		# that the closing bracket is NOT matched
		# this behavior is needed in order for the URLSequence to work
		self.assertEqual(URL.parseString('http://1)')[0], 'http://1')

	def test_URLSequence(self):
		s0 = "(sequence http://1 http://2 http://3)"
		s1 = "( sequence http://1 http://2 http://3 )"
		s2 = "(  sequence  http://1   http://2 http://3)"
		s3 = "(  sequence  http://1   http://2)"
		s4 = "(sequence http://130-000.eduroam.rwth-aachen.de:7778/acc )"
		res = ['http://1', 'http://2', 'http://3']
		self.assertEqual(list(URLSequence.parseString(s0)), res)
		self.assertEqual(list(URLSequence.parseString(s1)), res)
		self.assertEqual(list(URLSequence.parseString(s2)), res)
		self.assertEqual(list(URLSequence.parseString(s3)), ['http://1', 'http://2'])
		self.assertEqual(list(URLSequence.parseString(s4)), ['http://130-000.eduroam.rwth-aachen.de:7778/acc'])

	def test_AgentIdentifier(self):
		a0 = "( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ) )"
		a1 = "( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )"
		res0 = AgentIdentifier.parseString(a0)[0]
		self.assertEqual(res0['name'], 'rma@192.168.122.1:1099/JADE')
		self.assertEqual(list(res0['addresses']), ['http://130-000.eduroam.rwth-aachen.de:7778/acc'])
		self.assertEqual(list(AgentIdentifier.parseString(a1)[0]['addresses']), ['http://1', 'http://2'])

	def test_AgentIdentifierSet(self):
		s0 = "(set ( agent-identifier :name test  :addresses (sequence http://1 )) )"
		s1 = "(set ( agent-identifier :name test  :addresses (sequence http://1 ) ) )"
		s2 = "(  set ( agent-identifier :name test  :addresses ( sequence http://1 ) ) )"
		expect0 = {'name': 'test', 'addresses': ['http://1']}
		s3 = "(set ( agent-identifier :name t1  :addresses (sequence http://1 )) ( agent-identifier :name t2  :addresses (sequence http://2 )) )"
		expect3 = [{'name': 't1', 'addresses': ['http://1']}, {'name': 't2', 'addresses': ['http://2']}]
		self.assertEqual(AgentIdentifierSet.parseString(s0)[0], expect0)
		self.assertEqual(AgentIdentifierSet.parseString(s1)[0], expect0)
		self.assertEqual(AgentIdentifierSet.parseString(s2)[0], expect0)
		self.assertEqual(list(AgentIdentifierSet.parseString(s3)), expect3)

	def test_MessageParameter(self):
		self.assertRaises(ParseException, MessageParameter.parseString, ":sender wrong")
		self.assertRaises(ParseException, MessageParameter.parseString, ":sender 100")
		self.assertRaises(ParseException, MessageParameter.parseString, ":invalid ( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )")

		inp = ":sender ( agent-identifier :name test  :addresses (sequence http://1 http://2 ) )"
		out = MessageParameter.parseString(inp)

		self.assertTrue('sender' in out)
		self.assertEqual(out['sender'][0], {'name': 'test', 'addresses': ['http://1', 'http://2']})

		out = MessageParameter.parseString(":reply-by 20150701T143941567")
		self.assertTrue('reply-by' in out)
		self.assertEqual(out['reply-by'][0], datetime.datetime(2015, 7, 1, 14, 39, 41, 567 * 1000))

	def test_Message(self):
		msg = ('\n\n(REQUEST\n' +
			' :sender  ( agent-identifier :name rma@192.168.122.1:1099/JADE  :addresses (sequence http://130-000.eduroam.rwth-aachen.de:7778/acc ))\n' +
			' :receiver  (set ( agent-identifier :name test  :addresses (sequence http://localhost:9000 )) )\n' +
			' :content  "((action (agent-identifier :name test :addresses (sequence http://localhost:9000)) (get-description)))" \n' +
			' :language  fipa-sl0  :ontology  FIPA-Agent-Management  :protocol  fipa-request\n' +
			' :conversation-id  C1438784720_1435754381566 )\n\n\n')
		out = Message.parseString(msg)

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
