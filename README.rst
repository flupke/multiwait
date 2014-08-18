multiwait
=========

multiwait allows to run a command after conditions have been fulfilled. For
example you can use it to start a program after Redis has finished loading its
dataset into memory, or after a lock file has disappeared (or both).

The settings are given in a YAML file, for example:

.. code:: yaml

    defaults:
        timeout: 60

    conditions:
        - redis-dataset-loaded
        - file-absent:
            path: /path/to/lockfile
            warmup: 10
            test_interval: 1
        - file-present:
            path: /path/to/socket
            timeout: 15

Then you point the ``multiwait`` command to the settings and the command you
want to run::

    $ multiwait --settings /path/to/settings.yaml echo "foo"

Here ``echo foo`` will only be run once Redis has finished loading its dataset
in memory, the ``/path/to/lockfile`` has disappeared, and ``/path/to/socket``
exists.

The command will replace ``multiwait`` process, so it's safe to use in process
managers.

Conditions
==========

The conditions to fulfill before running the commands are described in the
``conditions`` key of the settings file. It must be a list containing
conditions definitions. Each entry must contain an object with the condition
name as the single key, and arguments to the definition. As a shortcut you can
also write the condition name alone if doesn't take arguments or you just want
to use the defaults; in the example above ``redis-dataset-loaded`` is a
shortcut for ``redis-dataset-loaded: {}``.

All conditions at least accept the following arguments:

timeout
    Maximum execution time for the condition, in seconds before giving up. The
    default is no timeout.

warmup
    Sleep for this amount of time before starting testing for the condition.
    The default is no warm-up time.

test_interval
    An interval in seconds between two tests. The default is 0.1 second.

Global default arguments can be specified in the ``defaults`` top-level key in
the settings file. They are overridden by the conditions-specific; in the
example above all conditions have a 60 seconds timeout, except ``file-present``
which has a 15 seconds timeout.

Built-in conditions
-------------------

redis-dataset-loaded

    Wait until Redis has finished loading its dataset in memory. Requires the
    `redis <https://pypi.python.org/pypi/redis>`_ package.

    * ``host``: the host of the Redis server (default: "localhost")
    * ``port``: the port number of the Redis server (default: 6379)
    * ``password``: the password used to connect to the Redis server (default:
      no password)

file-present

    Wait until a file is present on the filesystem.

    * ``path`` (required): the path of the file

file-absent

    Wait until a file is not present on the filesystem.

    * ``path`` (required): the path of the file
