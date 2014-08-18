import os
import os.path as op
import shutil

from nose.tools import assert_equal, assert_raises

from .. import modules
from ..modules.base import Condition
from ..modules.files import FilePresent, FileAbsent
from ..exceptions import Timeout


THIS_DIR = op.dirname(__file__)
TMP_DIR = op.join(THIS_DIR, 'tmp')


class DummyCondition(Condition):

    defaults = {'foo': 42}
    required = ['bar']

    def test(self):
        return True


class FaultyCondition(Condition):

    def test(self):
        1/0


modules.register('dummy', DummyCondition)
modules.register('faulty', FaultyCondition)


def setup():
    if op.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)


def test_files():
    path = op.join(TMP_DIR, 'file')
    file_present = FilePresent(path=path, timeout=1)
    assert_raises(Timeout, file_present.wait)
    open(path, 'w').close()
    file_present.wait()
    file_absent = FileAbsent(path=path, timeout=1)
    assert_raises(Timeout, file_absent.wait)
    os.unlink(path)
    file_absent.wait()


def test_init():
    assert_raises(TypeError, DummyCondition)
    assert_raises(TypeError, DummyCondition, bar=1, blah=2)
    cond = DummyCondition(bar=1, foo=2)
    assert_equal(cond.bar, 1)
    assert_equal(cond.foo, 2)


def test_repr():
    cond = DummyCondition(bar=1, foo=2)
    assert_equal(repr(cond), 'dummy(foo=2, bar=1)')


def test_wait_parallel():
    dummy = DummyCondition(bar=1)
    faulty = FaultyCondition()
    assert_equal(modules.wait_parallel([dummy]), True)
    assert_equal(modules.wait_parallel([dummy, dummy]), True)
    assert_equal(modules.wait_parallel([faulty]), False)
    assert_equal(modules.wait_parallel([dummy, faulty]), False)


def test_load_from_list():
    conditions = modules.load_from_list([
        'faulty',
        {'dummy': {'bar': 10}},
    ])
    assert_equal(type(conditions[0]), FaultyCondition)
    assert_equal(type(conditions[1]), DummyCondition)
    assert_equal(conditions[1].bar, 10)
