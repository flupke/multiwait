from __future__ import absolute_import

from . import register
from .base import Condition


class RedisDatasetLoaded(Condition):
    '''
    Wait until redis dataset has finished loading into memory.
    '''

    defaults = {
        'host': 'localhost',
        'port': 6379,
        'password': None,
    }

    def test(self):
        import redis

        client = redis.StrictRedis(host=self.host, port=self.port,
                password=self.password)
        try:
            client.dbsize()
        except redis.ResponseError as exc:
            if exc.args[0].startswith('LOADING'):
                return False
            else:
                raise
        else:
            return True


register('redis-dataset-loaded', RedisDatasetLoaded)
