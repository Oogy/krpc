import collections
from enum import Enum
import krpc.schema.KRPC

VALUE_TYPES = {
    krpc.schema.KRPC.Type.DOUBLE: float,
    krpc.schema.KRPC.Type.FLOAT: float,
    krpc.schema.KRPC.Type.SINT32: int,
    krpc.schema.KRPC.Type.SINT64: long,
    krpc.schema.KRPC.Type.UINT32: int,
    krpc.schema.KRPC.Type.UINT64: long,
    krpc.schema.KRPC.Type.BOOL: bool,
    krpc.schema.KRPC.Type.STRING: str,
    krpc.schema.KRPC.Type.BYTES: bytes
}

MESSAGE_TYPES = {
    krpc.schema.KRPC.Type.REQUEST: krpc.schema.KRPC.Request,
    krpc.schema.KRPC.Type.RESPONSE: krpc.schema.KRPC.Response,
    krpc.schema.KRPC.Type.STREAM_MESSAGE: krpc.schema.KRPC.StreamMessage,
    krpc.schema.KRPC.Type.STATUS: krpc.schema.KRPC.Status,
    krpc.schema.KRPC.Type.SERVICES: krpc.schema.KRPC.Services,
}

def _protobuf_type(code, service=None, name=None, types=None):
    protobuf_type = krpc.schema.KRPC.Type()
    protobuf_type.code = code
    if service is not None:
        protobuf_type.service = service
    if name is not None:
        protobuf_type.name = name
    if types is not None:
        protobuf_type.types.extend(types)
    return protobuf_type


class Types(object):
    """ A type store. Used to obtain type objects from protocol buffer type strings,
        and stores python types for services and service defined class and
        enumeration types. """

    def __init__(self):
        # Mapping from protobuf type strings to type objects
        self._types = {}

    def as_type(self, protobuf_type, doc=None):
        """ Return a type object given a protocol buffer type """

        # Get cached type
        key = protobuf_type.SerializeToString()
        if key in self._types:
            return self._types[key]

        # pylint: disable=redefined-variable-type
        if protobuf_type.code in VALUE_TYPES:
            typ = ValueType(protobuf_type)
        elif protobuf_type.code in MESSAGE_TYPES:
            typ = MessageType(protobuf_type)
        elif protobuf_type.code == krpc.schema.KRPC.Type.CLASS:
            typ = ClassType(protobuf_type, doc)
        elif protobuf_type.code == krpc.schema.KRPC.Type.ENUMERATION:
            typ = EnumerationType(protobuf_type, doc)
        elif protobuf_type.code == krpc.schema.KRPC.Type.TUPLE:
            typ = TupleType(protobuf_type, self)
        elif protobuf_type.code == krpc.schema.KRPC.Type.LIST:
            typ = ListType(protobuf_type, self)
        elif protobuf_type.code == krpc.schema.KRPC.Type.SET:
            typ = SetType(protobuf_type, self)
        elif protobuf_type.code == krpc.schema.KRPC.Type.DICTIONARY:
            typ = DictionaryType(protobuf_type, self)
        else:
            raise ValueError('Invalid type')
        # pylint: enable=redefined-variable-type

        self._types[key] = typ
        return typ

    @classmethod
    def is_none_type(cls, protobuf_type):
        return protobuf_type.code == krpc.schema.KRPC.Type.NONE

    @property
    def double_type(self):
        """ Get a double value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.DOUBLE))

    @property
    def float_type(self):
        """ Get a float value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.FLOAT))

    @property
    def sint32_type(self):
        """ Get an sint32 value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.SINT32))

    @property
    def sint64_type(self):
        """ Get an sint64 value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.SINT64))

    @property
    def uint32_type(self):
        """ Get a uint32 value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.UINT32))

    @property
    def uint64_type(self):
        """ Get a uint64 value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.UINT64))

    @property
    def bool_type(self):
        """ Get a bool value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.BOOL))

    @property
    def string_type(self):
        """ Get a string value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.STRING))

    @property
    def bytes_type(self):
        """ Get a bytes value type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.BYTES))

    def class_type(self, service, name, doc=None):
        """ Get a class type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.CLASS, service, name), doc=doc)

    def enumeration_type(self, service, name, doc=None):
        """ Get an enumeration type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.ENUMERATION, service, name), doc=doc)

    @property
    def request_type(self):
        """ Get a Request message type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.REQUEST))

    @property
    def response_type(self):
        """ Get a Response message type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.RESPONSE))

    @property
    def stream_message_type(self):
        """ Get a StreamMessage message type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.STREAM_MESSAGE))

    @property
    def status_type(self):
        """ Get a Status message type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.STATUS))

    @property
    def services_type(self):
        """ Get a Services message type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.SERVICES))

    def tuple_type(self, *value_types):
        """ Get a tuple type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.TUPLE, None, None,
                                           [t.protobuf_type for t in value_types]))

    def list_type(self, value_type):
        """ Get a list type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.LIST, None, None, [value_type.protobuf_type]))

    def set_type(self, value_type):
        """ Get a set type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.SET, None, None, [value_type.protobuf_type]))

    def dictionary_type(self, key_type, value_type):
        """ Get a dictionary type """
        return self.as_type(_protobuf_type(krpc.schema.KRPC.Type.DICTIONARY, None, None,
                                           [key_type.protobuf_type, value_type.protobuf_type]))

    def coerce_to(self, value, typ):
        """ Coerce a value to the specified type (specified by a type object).
            Raises ValueError if the coercion is not possible. """
        if isinstance(value, typ.python_type):
            return value
        # A unicode type can be coerced to a string
        if typ.python_type == str and isinstance(value, unicode):
            return value
        # A NoneType can be coerced to a ClassType
        if isinstance(typ, ClassType) and value is None:
            return None
        # Coerce identical class types from different client connections
        if isinstance(typ, ClassType) and isinstance(value, ClassBase):
            value_type = type(value)
            if (
                    typ.python_type._service_name == value_type._service_name
                    and typ.python_type._class_name == value_type._class_name
            ):
                return typ.python_type(value._object_id)
        # Collection types
        try:
            # Coerce tuples to lists
            if isinstance(value, collections.Iterable) and isinstance(typ, ListType):
                return typ.python_type(self.coerce_to(x, typ.value_type) for x in value)
            # Coerce lists (with appropriate number of elements) to tuples
            if isinstance(value, collections.Iterable) and isinstance(typ, TupleType):
                if len(value) != len(typ.value_types):
                    raise ValueError
                return typ.python_type([self.coerce_to(x, typ.value_types[i]) for i, x in enumerate(value)])
        except ValueError:
            raise ValueError('Failed to coerce value ' + str(value) + ' of type ' + str(type(value)) +
                             ' to type ' + str(typ))
        # Numeric types
        # See http://docs.python.org/2/reference/datamodel.html#coercion-rules
        numeric_types = (float, int, long)
        if (
                isinstance(value, bool)
                or not any(isinstance(value, t) for t in numeric_types)
                or typ.python_type not in numeric_types
        ):
            raise ValueError('Failed to coerce value ' + str(value) + ' of type ' + str(type(value)) +
                             ' to type ' + str(typ))
        if typ.python_type == float:
            return float(value)
        elif typ.python_type == int:
            return int(value)
        else:
            return long(value)


class TypeBase(object):
    """ Base class for all type objects """

    def __init__(self, protobuf_type, python_type, string):
        self._protobuf_type = protobuf_type
        self._python_type = python_type
        self._string = string

    @property
    def protobuf_type(self):
        """ Get the protocol buffer type string for the type """
        return self._protobuf_type

    @property
    def python_type(self):
        """ Get the python type """
        return self._python_type

    def __str__(self):
        return '<type: ' + str(self._string) + '>'


class ValueType(TypeBase):
    """ A protocol buffer value type """

    def __init__(self, protobuf_type):
        if protobuf_type.code not in VALUE_TYPES:
            raise ValueError('Not a value type')
        string = krpc.schema.KRPC.Type.TypeCode.Name(protobuf_type.code).lower()
        super(ValueType, self).__init__(protobuf_type, VALUE_TYPES[protobuf_type.code], string)


class ClassType(TypeBase):
    """ A class type, represented by a uint64 identifier """

    def __init__(self, protobuf_type, doc):
        if protobuf_type.code != krpc.schema.KRPC.Type.CLASS:
            raise ValueError('Not a class type')
        if not protobuf_type.service:
            raise ValueError('Class type has no service name')
        if not protobuf_type.name:
            raise ValueError('Class type has no class name')
        typ = _create_class_type(protobuf_type.service, protobuf_type.name, doc)
        string = 'Class(%s.%s)' % (protobuf_type.service, protobuf_type.name)
        super(ClassType, self).__init__(protobuf_type, typ, string)


class EnumerationType(TypeBase):
    """ An enumeration type, represented by an sint32 value """

    def __init__(self, protobuf_type, doc):
        if protobuf_type.code != krpc.schema.KRPC.Type.ENUMERATION:
            raise ValueError('Not an enum type')
        if not protobuf_type.service:
            raise ValueError('Enum type has no service name')
        if not protobuf_type.name:
            raise ValueError('Enum type has no class name')
        self._service_name = protobuf_type.service
        self._enum_name = protobuf_type.name
        self._doc = doc
        string = 'Enum(%s.%s)' % (protobuf_type.service, protobuf_type.name)
        # Sets python_type to None, set_values must be called to set the python_type
        super(EnumerationType, self).__init__(protobuf_type, None, string)

    def set_values(self, values):
        """ Set the python type. Creates an Enum class using the given values. """
        self._python_type = _create_enum_type(self._enum_name, values, self._doc)


class MessageType(TypeBase):
    """ A protocol buffer message type """

    def __init__(self, protobuf_type):
        if protobuf_type.code not in MESSAGE_TYPES:
            raise ValueError('Not a message type')
        typ = MESSAGE_TYPES[protobuf_type.code]
        super(MessageType, self).__init__(protobuf_type, typ, typ.__name__)


class TupleType(TypeBase):
    """ A tuple collection type """

    def __init__(self, protobuf_type, types):
        if protobuf_type.code != krpc.schema.KRPC.Type.TUPLE:
            raise ValueError('Not a tuple type')
        if len(protobuf_type.types) < 1:
            raise ValueError('Wrong number of sub-types for tuple type')
        self.value_types = [types.as_type(t) for t in protobuf_type.types]
        string = 'Tuple(%s)' % ','.join(t._string for t in self.value_types)
        super(TupleType, self).__init__(protobuf_type, tuple, string)


class ListType(TypeBase):
    """ A list collection type """

    def __init__(self, protobuf_type, types):
        if protobuf_type.code != krpc.schema.KRPC.Type.LIST:
            raise ValueError('Not a list type')
        if len(protobuf_type.types) != 1:
            raise ValueError('Wrong number of sub-types for list type')
        self.value_type = types.as_type(protobuf_type.types[0])
        string = 'List(%s)' % self.value_type._string
        super(ListType, self).__init__(protobuf_type, list, string)


class SetType(TypeBase):
    """ A set collection type """

    def __init__(self, protobuf_type, types):
        if protobuf_type.code != krpc.schema.KRPC.Type.SET:
            raise ValueError('Not a set type')
        if len(protobuf_type.types) != 1:
            raise ValueError('Wrong number of sub-types for set type')
        self.value_type = types.as_type(protobuf_type.types[0])
        string = 'Set(%s)' % self.value_type._string
        super(SetType, self).__init__(protobuf_type, set, string)


class DictionaryType(TypeBase):
    """ A dictionary collection type """

    def __init__(self, protobuf_type, types):
        if protobuf_type.code != krpc.schema.KRPC.Type.DICTIONARY:
            raise ValueError('Not a dictionary type')
        if len(protobuf_type.types) != 2:
            raise ValueError('Wrong number of sub-types for dictionary type')
        self.key_type = types.as_type(protobuf_type.types[0])
        self.value_type = types.as_type(protobuf_type.types[1])
        string = 'Dict(%s,%s)' % (self.key_type._string, self.value_type._string)
        super(DictionaryType, self).__init__(protobuf_type, dict, string)


class DynamicType(object):
    @classmethod
    def _add_method(cls, name, func, doc=None):
        """ Add a method """
        func.__name__ = name
        func.__doc__ = doc
        setattr(cls, name, func)
        return getattr(cls, name)

    @classmethod
    def _add_static_method(cls, name, func, doc=None):
        """ Add a static method """
        func.__name__ = name
        func.__doc__ = doc
        func = staticmethod(func)
        setattr(cls, name, func)
        return getattr(cls, name)

    @classmethod
    def _add_property(cls, name, getter=None, setter=None, doc=None):
        """ Add a property """
        if getter is None and setter is None:
            raise ValueError('Either getter or setter must be provided')
        prop = property(getter, setter, doc=doc)
        setattr(cls, name, prop)
        return getattr(cls, name)


class ClassBase(DynamicType):
    """ Base class for service-defined class types """

    _client = None

    def __init__(self, object_id):
        self._object_id = object_id

    def __eq__(self, other):
        return isinstance(other, ClassBase) and self._object_id == other._object_id

    def __ne__(self, other):
        return not isinstance(other, ClassBase) or self._object_id != other._object_id

    def __lt__(self, other):
        if not isinstance(other, ClassBase):
            raise NotImplementedError
        return self._object_id < other._object_id

    def __le__(self, other):
        if not isinstance(other, ClassBase):
            raise NotImplementedError
        return self._object_id <= other._object_id

    def __gt__(self, other):
        if not isinstance(other, ClassBase):
            raise NotImplementedError
        return self._object_id > other._object_id

    def __ge__(self, other):
        if not isinstance(other, ClassBase):
            raise NotImplementedError
        return self._object_id >= other._object_id

    def __hash__(self):
        return hash(self._object_id)

    def __repr__(self):
        return '<%s.%s remote object #%d>' % (self._service_name, self._class_name, self._object_id)


def _create_class_type(service_name, class_name, doc):
    return type(str(class_name), (ClassBase,),
                {'_service_name': service_name, '_class_name': class_name, '__doc__': doc})


def _create_enum_type(enum_name, values, doc):
    typ = Enum(str(enum_name), dict((name, x['value']) for name, x in values.items()))
    setattr(typ, '__doc__', doc)
    for name in values.keys():
        setattr(getattr(typ, name), '__doc__', values[name]['doc'])
    return typ


class DefaultArgument(object):
    """ A sentinel value for default arguments """

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value

    def __repr__(self):
        return self._value
