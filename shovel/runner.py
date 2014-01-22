from __future__ import print_function

import logging
from .tasks import Shovel
from .parser import parse
from . import help, logger


def run(*args):
    '''Run the normal shovel functionality'''
    import os
    import sys
    import argparse
    import pkg_resources
    # First off, read the arguments
    parser = argparse.ArgumentParser(description='Rake, for Python')

    parser.add_argument('method', help='The task to run')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
        help='Be extra talkative')
    parser.add_argument('--dry-run', dest='dryRun', action='store_true',
        help='Show the args that would be used')

    ver = pkg_resources.require('shovel')[0].version
    parser.add_argument('--version', action='version',
        version='Shovel v %s' % ver, help='print the version of Shovel.')

    # Parse our arguments
    if args:
        clargs, remaining = parser.parse_known_args(args=args)
    else:  # pragma: no cover
        clargs, remaining = parser.parse_known_args()

    if clargs.verbose:
        logger.setLevel(logging.DEBUG)

    args, kwargs = parse(remaining)

    # Import all of the files we want
    shovel = Shovel()
    for path in [
        os.path.expanduser('~/.shovel.py'),
        os.path.expanduser('~/.shovel')]:
        if os.path.exists(path):  # pragma: no cover
            shovel.read(path, os.path.expanduser('~/'))

    for path in ['shovel.py', 'shovel']:
        if os.path.exists(path):
            shovel.read(path)

    # If it's help we're looking for, look no further
    if clargs.method == 'help':
        print(help.shovel_help(shovel, *args, **kwargs))
    elif clargs.method:
        # Try to get the first command provided
        try:
            tasks = shovel.tasks(clargs.method)
        except KeyError:
            print('Could not find task "%s"' % clargs.method, file=sys.stderr)
            exit(1)

        if len(tasks) > 1:
            print('Specifier "%s" matches multiple tasks:' % clargs.method, file=sys.stderr)
            for task in tasks:
                print('\t%s' % task.fullname, file=sys.stderr)
            exit(2)

        task = tasks[0]
        if clargs.dryRun:
            print(task.dry(*args, **kwargs))
        else:
            task(*args, **kwargs)
