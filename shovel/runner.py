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
    if clargs.method == 'tasks':
        tasks = [(tsk.fullname, tsk.doc.replace('\n', ' '))
            for tsk in shovel.Task.find()]
        if not tasks:
            print('No tasks found!')
        else:
            width = 80
            import shutil
            try:
                width, height = shutil.get_terminal_size(fallback=(0, width))
            except AttributeError as e:
                pass
            max_name_len = max([len(e[0]) for e in tasks])
            for tsk, doc in tasks:
                pad = max_name_len + 2 - len(tsk)
                doclen = width - max_name_len - 5
                print('%s%s# %s' % (tsk, ' ' * pad, doc[:doclen]))
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
