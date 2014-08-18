import os
import sys
import argparse

import yaml

from . import modules


def main():
    # Parse command line
    parser = argparse.ArgumentParser(description='Wait for stuff to happen '
            'before running a command',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--settings', default='/etc/multiwait.yaml',
            help='Path to the settings file')
    parser.add_argument('command', help='The command to run')
    parser.add_argument('args', nargs=argparse.REMAINDER,
            help='The command arguments')
    options = parser.parse_args()

    # Load settings
    with open(options.settings) as fp:
        settings = yaml.load(fp)

    # Discover condition modules
    modules.discover()

    # Create conditions
    conditions = modules.load_from_list(settings['conditions'],
            settings.get('defaults', {}))

    # Wait for all conditions
    if not modules.wait_parallel(conditions):
        sys.exit(1)

    # Start command, replacing the current process
    args = [options.command] + options.args
    os.execvp(options.command, args)

