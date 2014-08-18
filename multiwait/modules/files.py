import os.path as op

from . import register
from .base import Condition


class FilePresent(Condition):

    required = ['path']

    def test(self):
        return op.isfile(self.path)


class FileAbsent(FilePresent):

    def test(self):
        return not super(FileAbsent, self).test()


register('file-present', FilePresent)
register('file-absent', FileAbsent)
