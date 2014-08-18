import pkgutil


def rimport(path):
    '''
    Works like :func:`__import__` but returns the last module instead of the first in
    the hierarchy, e.g. ``rimport('A.B')`` returns the module 'B'.
    '''
    return __import__(path, fromlist=[''])


def recursive_import(pkg):
    '''
    Import *pkg* and all its sub modules.

    *pkg* can be a dotted path or a module object.
    '''
    if isinstance(pkg, basestring):
        pkg = rimport(pkg)
    if not hasattr(pkg, '__path__'):
        # Not a package, we're done
        return
    for importer, name, ispkg in pkgutil.walk_packages(pkg.__path__,
            pkg.__name__ + '.'):
        __import__(name)

