import datetime
from functools import partial
import json
from urllib import urlencode
from urlparse import parse_qs, urlunsplit
import uuid

import riak

from makerbase import app


riakclient = riak.RiakClient(port=8087, transport_class=riak.RiakPbcTransport)


class LinkError(Exception):
    pass


class RobjectMetaclass(type):

    class_for_bucket = dict()

    def __new__(cls, name, bases, attr):
        if '_bucket' not in attr:
            attr['_bucket'] = name.lower()
        new_cls = type.__new__(cls, name, bases, attr)
        cls.class_for_bucket[attr['_bucket']] = new_cls
        return new_cls


class Link(object):

    def __init__(self, tag):
        self.tag = tag

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return instance.get_link(self.tag)


class LinkSet(object):

    def __init__(self, tag):
        self.tag = tag

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return instance.get_links(self.tag)


class Robject(object):

    __metaclass__ = RobjectMetaclass

    _bucket = None

    def __init__(self, *args, **kwargs):
        if args:
            self.id = args[0]
        if kwargs:
            self.__dict__.update(kwargs)
        self._after_store = list()

    @property
    def id(self):
        try:
            return self.__dict__['_id']
        except KeyError:
            ident = str(uuid.uuid1())
            self.__dict__['_id'] = ident
            return ident

    @id.setter
    def id(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self.__dict__['_id'] = value

    @classmethod
    def _new_for_entity(cls, entity):
        self = cls(entity.get_key(), **entity.get_data())
        self._entity = entity
        return self

    @classmethod
    def get(cls, ident):
        if isinstance(ident, unicode):
            ident = ident.encode('utf-8')
        entity = riakclient.bucket(cls._bucket).get(ident)
        if not entity or not entity.exists():
            app.logger.warning("Tried to load %s with id %r but found none", cls.__name__, ident)
            return None

        self = cls._new_for_entity(entity)
        app.logger.debug("Found for %s id %r entity %r! Returning %s %r!", cls._bucket, ident, entity, cls.__name__, self)
        return self

    def get_entity_data(self):
        return dict((k, v) for k, v in self.__dict__.iteritems() if not k.startswith('_'))

    def save(self):
        try:
            entity = self._entity
        except AttributeError:
            entity = riakclient.bucket(self._bucket).new(self.id, data=self.get_entity_data())
            self._entity = entity
        else:
            entity.set_data(self.get_entity_data())

        entity.store()

        after_store, self._after_store = self._after_store, list()
        for fn in after_store:
            fn()

    def delete(self):
        try:
            entity = self._entity
        except AttributeError:
            pass
        else:
            entity.delete()

    def get_link(self, tag):
        return self.get_links(tag).next()

    def get_links(self, tag):
        if tag is None:
            raise ValueError("A tag is required to get links with get_links()")
        try:
            entity = self._entity
        except AttributeError:
            return iter()
        return (RobjectMetaclass.class_for_bucket[link.get_bucket()]._new_for_entity(link.get()) for link in entity.get_links() if link.get_tag() == tag)

    def add_link(self, target, tag=None):
        try:
            entity = self._entity
        except AttributeError:
            self._after_store.append(partial(self.add_link, target, tag=tag))
            return
        try:
            target_entity = target._entity
        except AttributeError:
            target._after_store.append(partial(self.add_link, target, tag=tag))
            return
        entity.add_link(target_entity, tag=tag)


class Project(Robject):

    parties = LinkSet('participation')


class Maker(Robject):

    parties = LinkSet('participation')


class Participation(Robject):

    maker = Link('maker')
    project = Link('project')

    @property
    def start_date(self):
        return datetime.date(year=self.start_year, month=self.start_month + 1, day=1)

    @start_date.setter
    def start_date(self, dt):
        self.start_year = dt.year
        self.start_month = dt.month - 1

    @property
    def end_date(self):
        if not self.end_year:
            return
        return datetime.date(year=self.end_year, month=self.end_month + 1, day=1)

    @end_date.setter
    def end_date(self, dt):
        if dt is None:
            try:
                del self.end_year
            except AttributeError:
                pass
            try:
                del self.end_month
            except AttributeError:
                pass
            return
        self.end_year = dt.year
        self.end_month = dt.month - 1


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
