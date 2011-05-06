import transaction
from plumber import (
    plumber,
    Part,
    default,
    extend,
    finalize,
)
from odict.pyodict import (
    _odict,
    _nil,
)
from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from node.interfaces import (
    INode,
    IAttributes,
)
from node.parts import (
    Adopt,
    Nodespaces,
    Attributes,
    Order,
    AsAttrAccess,
    DefaultInit,
    Nodify,
    NodeChildValidate,
    Storage,
)
from node.utils import (
    AttributeAccess,
    instance_property,
)


class Podict(_odict, PersistentDict):
    
    def _dict_impl(self):
        return PersistentDict


class OOBTodict(_odict, OOBTree):
    
    def _dict_impl(self):
        return OOBTree
    
    def _get_lh(self):
        try:
            return self['____lh']
        except KeyError:
            self['____lh'] = _nil
        return self['____lh']

    def _set_lh(self, val):
        self['____lh'] = val

    lh = property(_get_lh, _set_lh)

    def _get_lt(self):
        try:
            return self['____lt']
        except KeyError:
            self['____lt'] = _nil
        return self['____lt']

    def _set_lt(self, val):
        self['____lt'] = val

    lt = property(_get_lt, _set_lt)
    
    def __getitem__(self, key):
        if key.startswith('____'):
            return self._dict_impl().__getitem__(self, key)
        return _odict.__getitem__(self, key)
    
    def __setitem__(self, key, val):
        if key.startswith('____'):
            # private attributes, no way to set persistent attributes on
            # OOBTree deriving class.
            self._dict_impl().__setitem__(self, key, val)
        else:
            _odict.__setitem__(self, key, val)
    
    def __repr__(self):
        if self:
            pairs = ("(%r, %r)" % (k, v) for k, v in self.iteritems())
            return "OOBTodict([%s])" % ", ".join(pairs)
        else:
            return "OOBTodict()"


class PodictStorage(Storage):
    
    @default
    @instance_property
    def storage(self):
        return Podict()


class OOBTodictStorage(Storage):
    
    @default
    @instance_property
    def storage(self):
        return OOBTodict()


class ZODBPart(Part):
    
    def _get_parent(self):
        if hasattr(self, '_parent'):
            return self._parent
        if hasattr(self, '_v_parent'):
            return self._v_parent
        return None
     
    def _set_parent(self, val):
        if isinstance(val, Persistent):
            self._parent = val
        else:
            self._v_parent = val
    
    __parent__ = extend(property(_get_parent, _set_parent))
    
    @extend
    def __getitem__(self, key):
        val = self.storage[key]
        if INode.providedBy(val):
            val.__parent__ = self
        return val
    
    @extend
    def __call__(self):
        transaction.commit()


class ZODBAttributes(Part):
    implements(IAttributes)
    
    attribute_access_for_attrs = default(False)
    attributes_factory = default(None)

    @finalize
    @property
    def attrs(self):
        try:
            attrs = self._attrs
        except AttributeError:
            self._attrs = attrs = self.attributes_factory(name='_attrs',
                                                          parent=self)
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs


class ZODBNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        DefaultInit,
        Nodify,
        ZODBPart,
        PodictStorage,
    )
    allow_non_node_childs = True


class ZODBNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        Order,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        ZODBAttributes,
        ZODBPart,
        PodictStorage,
    )
    attributes_factory = ZODBNodeAttributes
   
    
class OOBTNodeAttributes(Persistent):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        DefaultInit,
        Nodify,
        ZODBPart,
        OOBTodictStorage,
    )
    allow_non_node_childs = True


class OOBTNode(Persistent):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        Order,
        AsAttrAccess,
        DefaultInit,
        Nodify,
        ZODBAttributes,
        ZODBPart,
        OOBTodictStorage,
    )
    attributes_factory = OOBTNodeAttributes


def volatile_property(func):
    """Like ``node.utils.instance_property``, but sets instance attribute
    with '_v_' prefix.
    """
    def wrapper(self):
        attribute_name = '_v_%s' % func.__name__
        if not hasattr(self, attribute_name):
            setattr(self, attribute_name, func(self))
        return getattr(self, attribute_name)
    wrapper.__doc__ = func.__doc__
    return property(wrapper)