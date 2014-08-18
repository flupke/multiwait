import time
import multiprocessing
from multiprocessing.pool import ThreadPool
import traceback

from multiwait.exceptions import NameConflict
from multiwait.utils import recursive_import


_registry = {}


def register(name, condition):
    '''
    Register :class:`~multiwait.modules.base.Condition` class *condition* under
    *name*.
    '''
    if name in _registry:
        prev_condition = _registry[name]
        raise NameConflict('error registering %s.%s, %s.%s is already '
                'registered under the name %s' % (condition.__module__,
                    condition.__name__, prev_condition.__module__,
                    prev_condition.__name__, name))
    condition.__registered_name__ = name
    _registry[name] = condition


def get(name):
    '''
    Get :class:`~multiwait.modules.base.Condition` class registered under
    *name*.
    '''
    try:
        return _registry[name]
    except KeyError:
        return KeyError('unknown condition: %s' % name)


def load_from_list(data, defaults={}):
    '''
    Create a list of conditions objects from a list of definitions.

    Each entry in the list can be a condition name (as registered with
    :func:`get`), or a single item dict containing the condition name as the
    only key, and another dict with the condition parameters, e.g.::

        [
            'redis-dataset-loaded',
            {'file-absent': {'path': '/path/to/file'}}
        ]
    '''
    conditions = []
    for i, cond_spec in enumerate(data):
        if isinstance(cond_spec, basestring):
            condition = get(cond_spec)()
        elif isinstance(cond_spec, dict):
            name = cond_spec.keys()[0]
            args = cond_spec.values()[0]
            final_args = defaults.copy()
            final_args.update(args)
            cond_class = get(name)
            condition = cond_class(**final_args)
        else:
            raise TypeError('expected string or dict at index %s' % i)
        conditions.append(condition)
    return conditions


def discover():
    '''
    Discover all condition classes.
    '''
    recursive_import(__name__)


def wait_parallel(conditions):
    '''
    Wait for all *conditions* to be fulfilled.

    Conditions are run in parallel threads. Return a boolean indicating if all
    the conditions completed without raising an exception.
    '''
    # Run all conditions in a threads pool
    pool = ThreadPool(len(conditions))
    results = []
    for cond in conditions:
        result = pool.apply_async(cond.wait)
        results.append((cond, result))

    # Wait for conditions to finish and check for errors
    success = True
    for cond, result in results:
        # We do this strange while loop to poll AsyncResult.get() of just
        # calling AsyncResult.get(cond.timeout) to avoid blocking the main
        # thread when timeout is None, and respond to ctrl+c
        start_time = time.time()
        while (cond.timeout is None or
                time.time() - start_time < cond.timeout):
            try:
                result.get(0.1)
            except multiprocessing.TimeoutError:
                pass
            except:
                success = False
                print 'Error running %r:\n%s' % (cond, traceback.format_exc())
                break
            else:
                break
        else:
            success = False
            print '%r timed out' % cond
    return success

