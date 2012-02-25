import json
from urllib import urlencode
from urlparse import parse_qs, urlunsplit

import riak

from makerbase import app


riakclient = riak.RiakClient(port=8087, transport_class=riak.RiakPbcTransport)


class LinkError(Exception):
    pass


class RobjectMetaclass(type):

    def __new__(cls, name, bases, attr):
        if '_bucket' not in attr:
            attr['_bucket'] = name.lower()
        return type.__new__(cls, name, bases, attr)


class Robject(object):

    __metaclass__ = RobjectMetaclass

    _bucket = None

    def __init__(self, *args, **kwargs):
        if args:
            self.id = args[0]
        if kwargs:
            self.__dict__.update(kwargs)

    @classmethod
    def get(cls, userid):
        entity = riakclient.bucket(cls._bucket).get(userid.encode('utf-8'))
        if not entity or not entity.exists():
            app.logger.warning("Tried to load %s with id %r but found none", cls.__name__, userid)
            return None

        self = cls()
        self.__dict__.update(entity.get_data())
        self.id = userid
        self._entity = entity
        app.logger.debug("Found for %s id %r entity %r! Returning %s %r!", cls._bucket, userid, entity, cls.__name__, self)
        return self

    def get_entity_data(self):
        return dict((k, v) for k, v in self.__dict__.iteritems() if not k.startswith('_'))

    def save(self):
        try:
            entity = self._entity
        except AttributeError:
            entity = riakclient.bucket(self._bucket).new(self.id.encode('utf-8'), data=self.get_entity_data())
            self._entity = entity
        else:
            entity.set_data(self.get_entity_data())
        entity.store()

    def get_links(self, tag=None):
        try:
            entity = self._entity
        except AttributeError:
            return list()
        if tag is None:
            return entity.get_links()
        return (link for link in entity.get_links() if link.tag == tag)

    def add_link(self, target, tag=None):
        try:
            entity = self._entity
        except AttributeError:
            raise LinkError("Can't add link to %r as it doesn't yet have an entity" % self)
        try:
            target_entity = target._entity
        except AttributeError:
            raise LinkError("Can't add link pointing to %r as it doesn't yet have an entity" % self)
        entity.add_link(target_entity, tag=tag)


class Project(Robject):
    pass


class Maker(Robject):
    pass


class Participation(Robject):
    pass


class User(Robject):

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id


__all__ = ('Project', 'Maker', 'Participation', 'User')
