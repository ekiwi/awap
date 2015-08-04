#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# parser.py

"""
This python module is able to parse awap communication
definitions files.
Two passes will be used.
The first pass will commit all objects to memory.
The second pass will resolve all cross references.
"""

import os
import lxml.etree as ET

def determine_max_id(mod, ee, max_id_found):
	""" Tries to determine the max-id from max-id and or size arguments
	"""
	max_id = ee.get("max-id")
	size = ee.get("size")
	mod.passert(ee, max_id is not None or size is not None,
		"You need to define either a size or a max-id for reasons of backwards compatibility. " +
		'e.g. <{} max-id="{}" />'.format(ee.tag, max_id_found))
	if size is not None and max_id is not None:
		mod.passert(ee, int(max_id) == (1 << int(size))-1,
			'max-id="{}" does not match size="{}"'.format(max_id, size))
		return int(max_id)
	elif size is not None:
		return ((1 << int(size)) -1)
	elif max_id is not None:
		return int(max_id)

class ParserException(Exception):
	def __init__(self, file, element, message):
		with open(file) as ff:
			lines = ff.readlines()
			line = lines[element.sourceline - 1]
		msg = '\n'
		msg += 'File "{}", line {}\n'.format(file, element.sourceline)
		msg += '    ' + line
		msg += '    Error: "{}"'.format(message)
		super().__init__(msg)

class NamedCommunicationElement(object):
	def __init__(self, parent, node):
		self.node = node
		self.name = node.get('name')
		self.parent = parent
		self.mod = parent.module
		self.full_name = parent.register(self, self.name)

	def register(self, child, name):
		return self.parent.register(child, self.name + "." + name)

	@property
	def module(self):
		return self.mod


class Service(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.messages = []
		self.properties = []

		messages = node.find("messages")
		for msg_ee in messages:
			self.messages.append(Message(self, msg_ee))
		max_id_found = max([msg.id for msg in self.messages])
		self.max_message_id = determine_max_id(self.mod, messages, max_id_found)
		self.mod.passert(node, self.max_message_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_message_id))

		properties = node.find("properties")
		for prop_ee in properties:
			self.properties.append(Property(self, prop_ee))
		max_id_found = max([prop.id for prop in self.properties])
		self.max_property_id = determine_max_id(self.mod, properties, max_id_found)
		self.mod.passert(node, self.max_property_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_property_id))


class Message(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.id = int(node.get("id"))
		self.performative = node.get("performative")
		self.direction = node.get("direction")
		if self.direction == "txrx":
			self.direction = "rxtx"
		self.fields = []
		for field_ee in node:
			if field_ee.tag in ['int', 'uint']:
				self.fields.append(Int(self, field_ee))
			elif field_ee.tag in ['enum']:
				self.fields.append(EnumField(self, field_ee))

class Property(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.id = int(node.get("id"))

class Import(object):
	def __init__(self, mod, node):
		self.import_module = node.get("module")
		self.module = mod
		self.alias = node.get("as", self.import_module)
		self.node = node

class Int(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.unsigned = (node.tag == "uint")
		self.size = node.get("size")

class EnumField(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.type_name = node.get("type")

class EnumType(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.elements = []

		for el_ee in node:
			self.elements.append(EnumElement(self, el_ee))
		max_id_found = max([el.id for el in self.elements])
		self.max_id = determine_max_id(self.mod, node, max_id_found)
		self.mod.passert(node, self.max_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_id))

class EnumElement(NamedCommunicationElement):
	def __init__(self, parent, node):
		super().__init__(parent, node)
		self.id = int(node.get('id'))

class Module(object):
	SchemaSingleton = None

	def __init__(self, parser, name):
		path = os.path.dirname(os.path.realpath(__file__))
		self.schema_path = os.path.join(path, 'communication.xsd')
		if Module.SchemaSingleton is None:
			xml = ET.parse(self.schema_path)
			Module.SchemaSingleton = ET.XMLSchema(xml)
		self.xmlschema = Module.SchemaSingleton
		self.parser = parser
		self.name = name
		self.loaded = False
		self.filename = self._find_file()
		self.imports = []
		self.services = []
		self.enums = []
		self.index = {}		# this will hold all possible references

	def _find_file(self):
		# search for module file
		parts = self.name.split('.')
		parts[-1] += ".xml"
		base = os.path.join(*parts)
		for path in self.parser.path:
			filename = os.path.join(path, base)
			if os.path.isfile(filename):
				return filename
		raise Exception('File for module "{}" not found.\nPath: "{}"'.format(self.name, self.parser.path))

	def register(self, child, name):
		""" insert unique reference into index """
		full_name = self.name + "." + name
		if full_name in self.index:
			oc0 = self.index[full_name].node
			oc1 = child.node
			with open(self.filename) as ff:
				lines = ff.readlines()
				line0 = lines[oc0.sourceline - 1]
				line1 = lines[oc1.sourceline - 1]
			msg  = 'Duplicate Element "{}".\n'.format(name)
			msg += 'First occurence:\n'
			msg += '\tFile "{}", line {}\n'.format(self.filename, oc0.sourceline)
			msg += '\t\t' + line0
			msg += 'Second occurence:\n'
			msg += '\tFile "{}", line {}\n'.format(self.filename, oc1.sourceline)
			msg += '\t\t' + line1
			raise Exception(msg)
		else:
			self.index[full_name] = child
		return full_name

	@property
	def module(self):
		return self

	def resolve(self):
		print("resolve called on " + self.name)
		# 1.) build index using imports
		print("\n".join(self.index.keys()))

	def parse(self):
		# open xml file
		tree = ET.parse(self.filename)
		root = tree.getroot()

		# validate
		valid = self.xmlschema.assertValid(tree)

		# parse root element
		self.passert(root, root.get("version") == "0.1",
			"Only version 0.1 supported at the moment.")
		self.passert(root, root.get("module") == self.name,
			'Module atrribute "{}" does not match module name "{}"'.format(
				root.get("module"), self.name))

		# parse child elements
		for ee in root:
			if ee.tag == "import":
				self.imports.append(Import(self, ee))
			elif ee.tag == "service":
				self.services.append(Service(self, ee))
			elif ee.tag == "enum":
				self.enums.append(EnumType(self, ee))
			elif ee.tag is ET.Comment:
				pass	# ignore comments
			else:
				print('Warn: unknown tag "{}" in "{}" line {}'.format(ee.tag, self.filename, ee.sourceline))

	def passert(self, element, value, msg):
		""" Parser Assert """
		if not value:
			raise ParserException(self.filename, element, msg)


	def passert_attribute_exists(self, element, attributename):
		self.passert(element, element.get(attributename) is not None,
			"Element <{} /> is missing required attribute `{}`".format(
				element.tag, attributename))


class CommunicationParser(object):
	def __init__(self):
		self.path = []
		# list of modules that have been loaded
		self.modules= {}
		# track current context
		self._module = ""
		self._file = ""

	def parse(self, modules):
		self.modules= {}
		if not isinstance(modules, list):
			modules = [modules]
		# load all files and commit objects to memory
		for mod in modules:
			self._load(mod)
		# resolve references
		for mod in self.modules.values():
			mod.resolve()


	def _load(self, module):
		# make sure module is not already loaded
		if module in self.modules:
			return

		# create module object
		mod = Module(self, module)
		self.modules[module] = mod
		# parse module
		mod.parse()

		# load imported modules
		for imp in mod.imports:
			self._load(imp.import_module)


if __name__ == "__main__":
	path = os.path.dirname(os.path.realpath(__file__))
	exampl_path = os.path.abspath(os.path.join(path, '..', '..', 'examples', 'communication'))

	p = CommunicationParser()
	p.path.append(exampl_path)
	p.parse('service.temperature')
