import os
import sys
import argparse

import yaml

from . import modules


def main():
    # Parse command line
    parser = argparse.ArgumentParser(description='Wait for stuff to happen '
            'before running a command.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--settings', default='/etc/multiwait.yaml',
            help='Path to the settings file.')
    parser.add_argument('-c', '--check', metavar='CONDITION', action='append',
            dest='checks', help='Check for a condition. Use the form '
            'condition:arg1=value,arg2=value to pass parameters.')
    parser.add_argument('command', help='The command to run.', nargs='?')
    parser.add_argument('args', nargs=argparse.REMAINDER,
            help='The command arguments.')
    options = parser.parse_args()

    # Discover condition modules
    modules.discover()

    if options.checks:
        # Create default conditions from the check names passed in the command
        # line
        parsed_defaults = {}
        parsed_conditions = []
        for check in options.checks:
            cond_name, _, args = check.partition(':')
            args_items = [x for x in args.split(',') if x.strip()]
            if args_items:
                cond_args = {}
                for arg in args_items:
                    name, _, value = arg.partition('=')
                    cond_args[name] = value
            else:
                cond_args = {}
            parsed_conditions.append({cond_name: cond_args})
    else:
        # Create conditions from settings
        with open(options.settings) as fp:
            settings = yaml.safe_load(fp)
        parsed_conditions = settings['conditions']
        parsed_defaults = settings.get('defaults', {})

    conditions = modules.load_from_list(parsed_conditions, parsed_defaults)

    # Wait for all conditions
    if not modules.wait_parallel(conditions,
            print_results=not bool(options.command)):
        sys.exit(1)

    # Start command, replacing the current process
    if options.command:
        args = [options.command] + options.args
        os.execvp(options.command, args)

