# Copyright (c) 2011-2014 Moz
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function

import logging
from .tasks import Shovel, Task
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

    # Read in any tasks that have already been defined
    shovel.extend(Task.clear())

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
    elif clargs.method == 'tasks':
        tasks = list(v for _, v in shovel.items())
        if not tasks:
            print('No tasks found!')
        else:
            names = list(t.fullname for t in tasks)
            docs = list(t.doc for t in tasks)

            # The width of the screen
            width = 80
            import shutil
            try:
                width, _ = shutil.get_terminal_size(fallback=(0, width))
            except AttributeError:
                pass

            # Create the format with padding for the longest name, and to
            # accomodate the screen width
            format = '%%-%is # %%-%is' % (
                max(len(name) for name in names), width)
            for name, doc in zip(names, docs):
                print(format % (name, doc))
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
