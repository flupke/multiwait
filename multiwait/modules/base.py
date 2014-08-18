import time
import abc
import itertools

from ..exceptions import Timeout


class Condition(object):
    '''
    Base class for wait conditions.
    '''

    __metaclass__ = abc.ABCMeta
    defaults = {}
    required = []

    def __init__(self, warmup=0, timeout=None, test_interval=0.1, **kwargs):
        self.warmup = warmup
        self.timeout = timeout
        self.test_interval = test_interval
        for key, default in self.defaults.items():
            setattr(self, key, kwargs.pop(key, default))
        for key in self.required:
            try:
                setattr(self, key, kwargs.pop(key))
            except KeyError:
                raise TypeError('required argument missing: %s' % key)
        if kwargs:
            raise TypeError('invalid arguments: %s' % ', '.join(kwargs))

    def wait(self):
        '''
        Wait until the condition is fulfilled.
        '''
        time.sleep(self.warmup)
        start_time = time.time()
        while (self.timeout is None or
                time.time() - start_time < self.timeout):
            if self.test():
                break
            time.sleep(self.test_interval)
        else:
            raise Timeout('%r nof fulfilled after %.2f seconds' % (
                self, self.timeout))

    @abc.abstractmethod
    def test(self):
        '''
        The condition defined by this class is considered fulfilled when this
        method returns True.

        Must be reimplemented in subclasses.
        '''

    def __repr__(self):
        ret = getattr(self, '__registered_name__', '%s.%s' %
                (self.__class__.__module__, self.__class__.__name__))
        if self.defaults or self.required:
            ret += '(%s)' % ', '.join('%s=%s' % (a, getattr(self, a)) for a in
                    itertools.chain(self.defaults, self.required))
        return ret
