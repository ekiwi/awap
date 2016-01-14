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

def camelCase(identifier):
	return identifier[0].lower() + identifier[1:]

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

class CommunicationElement(object):
	def __init__(self, parent, node):
		self.node = node
		self.parent = parent
		self.mod = parent.module

	@property
	def module(self):
		return self.mod

	def to_dict(self):
		return { }

class NamedCommunicationElement(CommunicationElement):
	def __init__(self, parent, node, name=None):
		super(NamedCommunicationElement, self).__init__(parent, node)
		self.name = node.get('name') if name is None else name
		self.full_name = parent.register(self, self.name)

	def register(self, child, name):
		return self.parent.register(child, self.name + "." + name)

	def to_dict(self):
		return { 'name': self.name }

	def _check_ids(self, ids, max_id):
		id_offset = ((index - id) for index, id in enumerate(ids))
		consecutive = all(offset == 0 for offset in id_offset)
		self.mod.passert(self.node, consecutive,
			'Ids ({}) must be consecutive!'.format(list(ids)))
		max_id_found = ids[-1]
		self.mod.passert(self.node, max_id >= max_id_found,
			'Found id "{}", but the maximum id is "{}"!'.format(max_id_found, max_id))
		return True


class CommunicationType(object):
	"""
	Base class for enum, bool, byte, short, int
	"""
	@property
	def cpp_type(self):
		return "void"

	@property
	def cpp_unsigned_type(self):
		return "void"

	@property
	def java_type(self):
		return "void"

	@property
	def java_box(self):
		return "void"

	@property
	def max_value(self):
		return 0

	@property
	def min_value(self):
		return 0

	@property
	def size(self):
		return 0

	@property
	def type(self):
		return None

	@property
	def unsigned(self):
		return False

	def to_dict(self):
		dd = {}
		dd['size'] = self.size
		dd['max_value'] = self.max_value
		dd['min_value'] = self.min_value
		dd['unsigned'] = self.unsigned
		dd['cpp'] = { 'type': self.cpp_type, 'unsigned_type': self.cpp_unsigned_type }
		dd['java'] = { 'type': self.java_type, 'box': self.java_box}
		dd['is_enum'] = 'enum' in self.type
		dd['is_bool'] = 'bool' in self.type
		return dd


class BooleanType(CommunicationType):
	@property
	def cpp_type(self):
		return "bool"

	@property
	def cpp_unsigned_type(self):
		return "uint8_t"

	@property
	def java_type(self):
		return "boolean"

	@property
	def java_box(self):
		return "Boolean"

	@property
	def max_value(self):
		return 1

	@property
	def min_value(self):
		return 0

	@property
	def size(self):
		return 1

	@property
	def type(self):
		return "bool"


class IntType(CommunicationType):
	def __init__(self, java_type):
		self._java_type = java_type
		assert(self._java_type in ['byte', 'short', 'int'])
		self._size = {'byte': 1, 'short': 2, 'int': 4}[self._java_type]

	@property
	def cpp_type(self):
		return 'int{}_t'.format(self.size * 8)

	@property
	def cpp_unsigned_type(self):
		return "u" + self.cpp_type

	@property
	def java_type(self):
		return self._java_type

	@property
	def java_box(self):
		return {'byte': 'Byte', 'short': 'Short', 'int': 'Integer'}[self.java_type]

	@property
	def max_value(self):
		return (1 << (self.size * 8 -1)) - 1

	@property
	def min_value(self):
		return - (self.max_value + 1)

	@property
	def size(self):
		return self._size

	@property
	def type(self):
		return self._java_type

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

class EnumType(NamedCommunicationElement, CommunicationType):
	def __init__(self, parent, node):
		super(EnumType, self).__init__(parent, node)
		self.elements = []
		self.max_id = 255	# enums will be sent as bytes

		for el_ee in node:
			self.elements.append(EnumElement(self, el_ee))
		self.elements.sort(key=lambda ee: ee.id)
		# make sure ids are consecutive
		self._check_ids([ee.id for ee in self.elements], self.max_id)

	@property
	def cpp_type(self):
		return "uint8_t"

	@property
	def cpp_unsigned_type(self):
		return self.cpp_type

	@property
	def java_type(self):
		return "short"

	@property
	def java_box(self):
		return "Short"

	@property
	def max_value(self):
		return 255

	@property
	def min_value(self):
		return 0

	@property
	def size(self):
		return 8

	@property
	def type(self):
		return "enumtype"

	def to_dict(self):
		dd = super(EnumType, self).to_dict()
		dd.update(CommunicationType.to_dict(self))
		dd['elements'] = [element.to_dict() for element in self.elements]
		dd['max_id'] = self.max_id
		dd['enum_name'] = self.name
		return dd

class EnumElement(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(EnumElement, self).__init__(parent, node)
		self.id = int(node.get('id'))

	def to_dict(self):
		dd = super(EnumElement, self).to_dict()
		dd['id'] = self.id
		return dd

class CommunicationField(NamedCommunicationElement):
	Boolean = BooleanType()
	Integer = IntType('int')
	Short   = IntType('short')
	Byte    = IntType('byte')
	Types   = {'bool': Boolean, 'byte': Byte, 'short': Short, 'int': Integer}

	def __init__(self, parent, node):
		assert(node.tag in ['bool', 'byte', 'short', 'int', 'enum'])
		super(CommunicationField, self).__init__(parent, node)
		self.id = int(node.get("id"))
		if node.tag == 'enum':
			self._type = Reference(self.mod, node, node.get("class"))
		else:
			self._type = CommunicationField.Types[node.tag]

	@property
	def type(self):
		if isinstance(self._type, Reference):
			return self._type.value
		else:
			return self._type

	@property
	def size(self):
		return self.type.size

	def to_dict(self):
		# copy type information
		dd = self.type.to_dict()
		dd.update(super(CommunicationField, self).to_dict())
		dd['id'] = self.id
		return dd


class FieldContainer(NamedCommunicationElement):
	"""
	Base class for properties and message elements in XML
	"""
	def __init__(self, parent, node, name=None):
		super(FieldContainer, self).__init__(parent, node, name)
		self.fields = [CommunicationField(self, field_node) for field_node in node]
		if len(self.fields) > 0:
			self.max_id = max(field.id for field in self.fields)
		else:
			self.max_id = -1

	def to_dict(self):
		dd = super(FieldContainer, self).to_dict()
		dd.update({'java': {'args': [] }, 'cpp': {'args': [] } })
		dd['fields'] = [field.to_dict() for field in self.fields]
		if len(self.fields) > 0:
			dd['java']['arg_names'] = [camelCase(field.name) for field in self.fields]
			dd['java']['args_list'] = ", " + ", ".join(dd['java']['arg_names'])
			dd['java']['args'] = ["{} {}".format(field.type.java_type, camelCase(field.name)) for field in self.fields]
			dd['cpp']['args']  = ["{} {}".format(field.type.cpp_type,  camelCase(field.name)) for field in self.fields]
			dd['java']['initializer_list'] = ", " + ", ".join(dd['java']['args'])
			dd['cpp']['initializer_list'] = ", " + ", ".join(dd['cpp']['args'])
		dd['bytes']  = sum(field.type.size for field in self.fields)
		dd['max_id'] = self.max_id
		return dd

class Message(FieldContainer):
	def __init__(self, parent, node):
		FieldContainer.__init__(self, parent, node)
		self.id = int(node.get("id"))
		self.performative = node.get("performative").replace('-', '_')
		direction = node.get("direction")
		self.tx = "tx" in direction
		self.rx = "rx" in direction

	def to_dict(self):
		dd = FieldContainer.to_dict(self)
		dd.update(NamedCommunicationElement.to_dict(self))
		dd['id'] = self.id
		dd['performative'] = self.performative
		dd['service'] = self.parent.name
		dd['tx'] = self.tx
		dd['rx'] = self.rx
		return dd

class Service(NamedCommunicationElement):
	def __init__(self, parent, node):
		super(Service, self).__init__(parent, node)
		self.id = -1    # needs to be set on a per configuration basis
		                # the external code is responsible for avoiding clashes
		self.messages = []
		self.properties = None

		messages = node.find("messages")
		for msg_ee in messages:
			if msg_ee.tag is not ET.Comment:
				self.messages.append(Message(self, msg_ee))
		self._check_ids([msg.id for msg in self.messages], 255)

		properties = node.find("properties")
		self.properties = FieldContainer(self, properties, "properties") if properties is not None else None
		self._check_ids([prop.id for prop in self.properties.fields], 255)

	def to_dict(self):
		dd = super(Service, self).to_dict()
		if self.id >= 0:
			dd['id'] = self.id
		dd['messages']   = [msg.to_dict() for msg  in self.messages]
		dd['max_message_id']  = max(msg.id for msg in self.messages)
		dd['properties'] = self.properties.to_dict()
		dd['properties_bytes'] = dd['properties']['bytes']
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
				enum_fields = (ff for ff in msg.fields if isinstance(ff.type, EnumType))
				for ff in enum_fields:
					if not ff.type in enums:
						enums.append(ff.type)
			for prop in service.properties.fields:
				properties.append(prop)
				if isinstance(prop.type, EnumType) and not prop.type in enums:
					enums.append(prop.type)
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
			                   for prop in service.properties.fields]
			output['modules'].append(dd)
		# create other dicts
		output['messages']   = [msg.to_dict()  for msg  in messages]
		output['properties'] = [prop.to_dict() for prop in properties]
		output['services']   = [serv.to_dict() for serv in services]
		output['enums']      = [enum.to_dict() for enum in enums]
		output['max_properties_size'] = max(serv['properties_bytes'] for serv in output['services'])
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
