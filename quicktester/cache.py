import uuid
import time
import json


class ExpiredError(Exception):
    pass


class _CacheEntry(object):
    def __init__(self, time, content):
        self.time = time
        self.content = content

    def to_json(self):
        return {'time': self.time, 'content': self.content}

    @classmethod
    def from_json(cls, value):
        return cls(value['time'], value['content'])


class Loader(object):
    def get_ident(self):
        raise NotImplementedError('{}.get_ident'.format(type(self).__name__))

    def get_time(self):
        raise NotImplementedError('{}.get_time'.format(type(self).__name__))

    def __call__(self):
        raise NotImplementedError('{}.__call__'.format(type(self).__name__))


class Cache(object):
    def __init__(self):
        self.__storage = {}

    def __call__(self, loader):
        ident = loader.get_ident()
        time = loader.get_time()
        if ident not in self.__storage or self.__storage[ident].time < time:
            content = loader()
            self.__storage[ident] = _CacheEntry(time, content)

        return self.__storage[ident].content

    def save(self, dest):
        json.dump(
            {str(ident): entry.to_json() for ident, entry in self.__storage.items()},
            dest
        )

    def load(self, source):
        self.__storage.update(
            (int(ident), _CacheEntry.from_json(value)) for ident, value in json.load(source).items()
        )
