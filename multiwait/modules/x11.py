from __future__ import absolute_import

import getpass
import time
import os.path as op
import subprocess
import errno

from . import register
from .base import Condition


class X11Running(Condition):
    '''
    Wait until X11 is up and running for the current user.

    This check needs password-less sudo access for GDM Xauth cookies.
    '''

    defaults = {
        'default_display': ':0',
    }

    def test(self):
        # Sometimes Xauth is not needed
        env = {'DISPLAY': self.default_display}
        if check_x11(env):
            return True

        # Search for Xauth cookie files
        xauth_paths = []
        default_xauth_path = op.expanduser('~/.Xauthority')
        if op.isfile(default_xauth_path):
            xauth_paths.append(default_xauth_path)
        if op.isdir('/var/run/gdm'):
            try:
                output = subprocess.check_output(['sudo', 'ls', '/var/run/gdm'])
                entries = output.split()
            except subprocess.CalledProcessError:
                pass
            else:
                user = getpass.getuser()
                for entry in entries:
                    if entry.startswith('auth-for-%s' % user):
                        xauth_paths.append('/var/run/gdm/%s/database' % entry)
                        break

        # Try to connect with Xauth cookies
        for xauth_path in xauth_paths:
            try:
                output = subprocess.check_output(['xauth', '-in', '-f',
                    xauth_path, 'list'])
            except subprocess.CalledProcessError:
                pass
            else:
                env = {
                    'DISPLAY': ':%s' % output.split()[0].rpartition(':')[2],
                    'XAUTHORITY': xauth_path,
                }
                if check_x11(env):
                    return True

        return False


register('x11-running', X11Running)


def check_x11(env, timeout=3):
    '''
    Verify that we can connect to X with *env* environment dict.

    Return a boolean indicating if the connection succeeded before *timeout*.
    '''
    with open(op.devnull, 'w') as devnull:
        process = subprocess.Popen(['xdpyinfo'], env=env, stdout=devnull,
                stderr=devnull)
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if process.poll() == 0:
                    return True
                elif process.poll() is not None:
                    break
                time.sleep(0.1)
            return False
        finally:
            end_process(process)


def end_process(process, timeout=3):
    '''
    Send SIGTERM to the process, wait for *timeout*, and send SIGKILL if it has
    not ended yet.
    '''
    try:
        process.terminate()
    except OSError, err:
        if err.errno == errno.ESRCH:
            # Nothing to kill
            return
        else:
            raise
    start_time = time.time()
    while time.time() - start_time < timeout:
        if process.poll() is not None:
            break
        time.sleep(0.1)
    else:
        try:
            process.kill()
        except OSError, err:
            if err.errno == errno.ESRCH:
                # Nothing to kill
                return
            else:
                raise
    process.wait()
