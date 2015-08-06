#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# parser.py
# Copyright (c) 2015, Kevin Laeufer <kevin.laeufer@rwth-aachen.de>

"""
This python module is able to parse awap communication
definitions files.
Two passes will be used.
The first pass will commit all objects to memory.
The second pass will resolve all cross references.
"""

import os, math
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
		super(ParserException, self).__init__(msg)

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

	def to_dict(self):
		return {
			'name': self.name,
			'full_name': self.full_name,
			'cpp':  {'name': self.full_name.replace('.', '::')},
			'java': {'name': self.full_name }
		}


class Service(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(Service, self).__init__(parent, node)
		self.id = -1    # needs to be set on a per configuration basis
		                # the external code is responsible for avoiding clashes
		self.messages = []
		self.properties = []

		messages = node.find("messages")
		for msg_ee in messages:
			if msg_ee.tag is not ET.Comment:
				self.messages.append(Message(self, msg_ee))
		max_id_found = max([msg.id for msg in self.messages])
		self.max_message_id = determine_max_id(self.mod, messages, max_id_found)
		self.mod.passert(node, self.max_message_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_message_id))

		properties = node.find("properties")
		for prop_ee in properties:
			if prop_ee.tag in ['int', 'uint']:
				self.properties.append(IntProperty(self, prop_ee))
			elif prop_ee.tag in ['enum']:
				self.properties.append(EnumProperty(self, prop_ee))
		if len(self.properties) > 0:
			max_id_found = max([prop.id for prop in self.properties])
		else:
			max_id_found = 0
		self.max_property_id = determine_max_id(self.mod, properties, max_id_found)
		self.mod.passert(node, self.max_property_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_property_id))

	def to_dict(self):
		dd = super(Service, self).to_dict()
		if self.id >= 0:
			dd['id'] = self.id
		dd['messages']   = [msg.to_dict()  for msg  in self.messages]
		dd['max_message_id']  = self.max_message_id
		dd['message_id_size'] = int(math.log(self.max_message_id,2) + 1)
		dd['properties'] = [prop.to_dict() for prop in self.properties]
		dd['max_property_id']  = self.max_property_id
		dd['property_id_size'] = int(math.log(self.max_property_id,2) + 1)
		return dd

class Message(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(Message, self).__init__(parent, node)
		self.id = int(node.get("id"))
		self.performative = node.get("performative")
		direction = node.get("direction")
		self.tx = "tx" in direction
		self.rx = "rx" in direction
		self.fields = []
		for field_ee in node:
			if field_ee.tag in ['int', 'uint']:
				self.fields.append(IntField(self, field_ee))
			elif field_ee.tag in ['enum']:
				self.fields.append(EnumField(self, field_ee))

	def to_dict(self):
		dd = super(Message, self).to_dict()
		dd['id'] = self.id
		dd['performative'] = self.performative
		dd['tx'] = self.tx
		dd['rx'] = self.rx
		dd['fields'] = [field.to_dict() for field in self.fields]
		return dd

class IntField(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(IntField, self).__init__(parent, node)
		self.unsigned = (node.tag == "uint")
		self.size = int(node.get("size"))

	def cpp_type(self):
		if self.size <= 8:    tt = "int8_t"
		elif self.size <= 16: tt = "int16_t"
		elif self.size <= 32: tt = "int32_t"
		return ("u" + tt) if self.unsigned else tt

	def java_type(self):
		# there seem to be no unsigened Java types, therefore we need
		# one bit more, if our input was a positive number
		if self.unsigned: size = self.size - 1
		else:             size = self.size
		if size <= 8:    return "byte"
		elif size <= 16: return "short"
		elif size <= 32: return "int"

	def to_dict(self):
		dd = super(IntField, self).to_dict()
		dd['unsigned'] = self.unsigned
		dd['size'] = self.size
		dd['cpp']  = {'type': self.cpp_type()}
		dd['java'] = {'type': self.java_type()}
		return dd

class EnumField(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(EnumField, self).__init__(parent, node)
		self.enum_class = Reference(self.mod, node, node.get("class"))

	def to_dict(self):
		dd = super(EnumField, self).to_dict()
		dd['size'] = self.enum_class.value.size
		dd['cpp'] = { 'type': self.enum_class.value.name }
		dd['java'] = { 'type': self.enum_class.value.java_type() }
		return dd

class IntProperty(IntField):
	def __init__(self, parent, node):
		super(IntProperty, self).__init__(parent, node)
		self.id = int(node.get("id"))

	def to_dict(self):
		dd = super(IntProperty, self).to_dict()
		dd['id'] = self.id
		return dd

class EnumProperty(EnumField):
	def __init__(self, parent, node):
		super(EnumProperty, self).__init__(parent, node)
		self.id = int(node.get("id"))

	def to_dict(self):
		dd = super(EnumProperty, self).to_dict()
		dd['id'] = self.id
		return dd

class Reference(object):
	def __init__(self, module, node, name):
		self.node = node # for error reporting
		self.name = name
		self.value = None
		module.references.append(self)

	def resolve(self, mod):
		mod.passert(self.node, self.name in mod.combined_index,
			'Could not resolve reference to "{}"'.format(self.name))
		self.value = mod.combined_index[self.name]

class EnumType(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(EnumType, self).__init__(parent, node)
		self.elements = []

		for el_ee in node:
			self.elements.append(EnumElement(self, el_ee))
		self.elements.sort(key=lambda ee: ee.id)
		# make sure ids are consecutive
		id_offset = ((index - ee.id) for index, ee in enumerate(self.elements))
		consecutive = all(offset == 0 for offset in id_offset)
		self.mod.passert(node, consecutive,
			'Ids ({}) must be consecutive!'.format([ee.id for ee in self.elements]))
		max_id_found = self.elements[-1].id
		self.max_id = determine_max_id(self.mod, node, max_id_found)
		self.mod.passert(node, self.max_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, self.max_id))

	@property
	def size(self):
		return int(math.log(self.max_id,2) + 1)

	def java_type(self):
		if self.size <= 8:    return "byte"
		elif self.size <= 16: return "short"
		elif self.size <= 32: return "int"

	def to_dict(self):
		dd = super(EnumType, self).to_dict()
		dd['elements'] = [element.to_dict() for element in self.elements]
		dd['size'] = self.size
		dd['max_id'] = self.max_id
		dd['cpp'] = { 'type': self.name }
		dd['java'] = { 'type': self.java_type() }
		return dd

class EnumElement(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(EnumElement, self).__init__(parent, node)
		self.id = int(node.get('id'))

	def to_dict(self):
		dd = super(EnumElement, self).to_dict()
		dd['id'] = self.id
		return dd

class Import(object):
	def __init__(self, mod, node):
		self.import_module_name = node.get("module")
		self.module = mod
		self.alias = node.get("as", self.import_module_name)
		self.node = node
		# will later be filled in by the parser
		self.import_module = None

	def add_to_index(self, index):
		prefix = (self.alias + ".") if len(self.alias) > 0 else ""
		for key, value in self.import_module.index.items():
			index[prefix + key] = value

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
		self.filename = self._find_file()
		self.imports = []
		self.services = {}
		self.enums = {}
		self.references = []	# will be resolved in the `resolve` stage
		# this will hold all possible references in this module
		self.index = {}
		# this will contain all references available in this module
		# as well as from other modules
		self.combined_index = {}

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
		if name in self.index:
			oc0 = self.index[name].node
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
			self.index[name] = child
		return name

	@property
	def module(self):
		return self

	def resolve(self):
		# 1.) build combined index
		self.combined_index = self.index.copy()
		[imp.add_to_index(self.combined_index) for imp in self.imports]
		# 2.) call resolve on references
		[ref.resolve(self) for ref in self.references]

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
				service = Service(self, ee)
				self.services[service.name] = service
			elif ee.tag == "enum":
				enum = EnumType(self, ee)
				self.enums[enum.name] = enum
			elif ee.tag is ET.Comment:
				pass	# ignore comments
			else:
				print('Warn: unknown tag "{}" in "{}" line {}'.format(ee.tag, self.filename, ee.sourceline))

	def to_dict(self):
		dd = {'name': self.name, 'filename': self.filename }
		dd['services'] = [service.to_dict() for service in self.services.values()]
		dd['enums'] = [enum.to_dict() for enum in self.enums.values()]
		dd['messages'] = [msg.to_dict() for service in self.services.values() for msg in service.messages]
		return dd

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
			return self.modules[module]

		# create module object
		mod = Module(self, module)
		self.modules[module] = mod
		# parse module
		mod.parse()

		# load imported modules
		for imp in mod.imports:
			imp.import_module = self._load(imp.import_module_name)

		return mod

	def get_dict(self, required_services, required_enums=[]):
		""" Returns a dictionary that contains all elements required
		    by the `services` and `enums` specified as well as the
		    `services` and `enums` themselves.
		"""
		# reference lists
		modules = []
		messages = []
		properties = []
		services = []
		enums = []
		# collect messages, properties and services
		# as well as enums that a message or property depends on
		for service_name in required_services:
			mod = self.modules[service_name.rsplit('.', 1)[0]]
			if not mod in modules: modules.append(mod)
			service = mod.services[service_name.rsplit('.', 1)[1]]
			services.append(service)
			# a service can depend on enums
			for msg in service.messages:
				messages.append(msg)
				enum_fields = (ff for ff in msg.fields if isinstance(ff, EnumField))
				for ff in enum_fields:
					if not ff.enum_class.value in enums:
						enums.append(ff.enum_class.value)
			for prop in service.properties:
				properties.append(prop)
				if isinstance(prop, EnumProperty) and not prop.enum_class.value in enums:
					enums.append(prop.enum_class.value)
		# collect enums that are required
		for enum_name in required_enums:
			mod = self.modules[enum_name.rsplit('.', 1)[0]]
			if not mod in modules: modules.append(mod)
			enum = mod.enums[enum_name.rsplit('.', 1)[1]]
			if not enum in enums:
				enums.append(enum)
		# the return dictionary
		output = { 'modules': [], 'messages': None, 'properties': None, 'services': None, 'enums': None }
		# create module dictionaries
		# unfortunately we cannot use the `to_dict` method, as this would
		# create a dictionary of the complete module
		# here we only want the subset, that is required, in order to
		# avoid including unused enums in our library
		for module in modules:
			dd = {'name': module.name, 'filename': module.filename }
			dd['services'] = [serv.to_dict() for serv
			                  in module.services.values() if serv in services]
			dd['enums'] = [enum.to_dict() for enum
			               in module.enums.values() if enum in enums]
			dd['messages'] = [msg.to_dict() for serv
			                  in module.services.values() if serv in services
			                  for msg in service.messages]
			dd['properties']= [prop.to_dict() for serv
			                   in module.services.values() if serv in services
			                   for prop in service.properties]
			output['modules'].append(dd)
		# create other dicts
		output['messages']   = [msg.to_dict()  for msg  in messages]
		output['properties'] = [prop.to_dict() for prop in properties]
		output['services']   = [serv.to_dict() for serv in services]
		output['enums']      = [enum.to_dict() for enum in enums]
		return output

if __name__ == "__main__":
	path = os.path.dirname(os.path.realpath(__file__))
	exampl_path = os.path.abspath(os.path.join(path, '..', '..', 'examples', 'communication'))

	p = CommunicationParser()
	p.path.append(exampl_path)
	p.parse('service.temperature')

#	for key, value in p.modules.items():
#		print("--------------------------------")
#		print("Module: {}".format(key))
#		print(value.to_dict())

	import pprint
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(p.get_dict(['service.temperature.TemperatureService']))
