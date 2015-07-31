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


class Service(object):
	def __init__(self, mod, ee):
		name = ee.get("name")
		mod.passert(ee, (name not in mod.services),
			'Service "{}" was already defined!'.format(name))
		self.ee = ee
		self.module = mod
		self.name = name
		self.messages = []
		self.propterties = []
		self.parse(self.module, self.ee)

	def _determine_max_id(self, mod, ee, max_id_found):
		max_id = ee.get("max-id")
		size = ee.get("size")
		mod.passert(ee, max_id is not None or size is not None,
			"You need to define either a size or a max-id for reasons of backwards compatibility. " +
			'e.g. <{} max-id="{}" />'.format(ee.tag, max_id_found))
		if size 

	def parse(self, mod, ee):
		mod.passert_singleton(ee, "messages")
		messages = ee.find("messages")
		for msg_ee in messages:
			self.messages.append(Message(mod, self, msg_ee))
		max_id_found = max([msg.id for msg in self.messages])
		self.max_message_id = self._determine_max_id(mod, messages, max_id_found)

		mod.passert_singleton(ee, "properties")
		properties = ee.find("messages")



class Message(object):
	def __init__(self, mod, service, ee):
		self.ee = ee
		self.module = mod
		self.service = service
		self.id = int(ee.get("id"))

class Import(object):
	def __init__(self, mod, ee):
		self.import_module = ee.get("module", None)
		mod.passert(ee, self.import_module is not None, 'Missing `module` attribute!')
		self.module = mod
		self.alias = ee.get("as", self.import_module)
		self.ee = ee


class Context(object):
	def __init__(self, module):
		self.module = module
		self.imports = []

#	def import(self, module, as=None):
#		if as is not None:
#			self.imports.append(())

class Module(object):
	def __init__(self, parser, name):
		self.parser = parser
		self.name = name
		self.loaded = False
		self.filename = self._find_file()
		self.imports = []
		self.services = []

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

	def parse(self):
		# open xml file
		tree = ET.parse(self.filename)
		root = tree.getroot()

		# parse root element
		self.passert_tagname(root, "awap-communication")
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
			elif ee.tag is ET.Comment:
				pass	# ignore comments
			else:
				print('Warn: unknown tag "{}" in "{}" line {}'.format(ee.tag, self.filename, ee.sourceline))

	def passert(self, element, value, msg):
		""" Parser Assert """
		if not value:
			raise ParserException(self.filename, element, msg)

	def passert_tagname(self, element, tagname):
		self.passert(element, element.tag == tagname,
			"Expected <{} /> found <{} />".format(tagname, element.tag))

	def passert_attribute_exists(self, element, attributename):
		self.passert(element, element.get(attributename) is not None,
			"Element <{} /> is missing required attribute `{}`".format(
				element.tag, attributename))

	def passert_singleton(self, element, childname):
		children = element.findall(childname)
		self.passert(element, len(children) <= 1,
			'Only one <{} /> tag allowed. Found tags @ line {}.'.format(
				childname,
				" and ".join([str(cc.sourceline) for cc in children])))


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
		# TODO


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
