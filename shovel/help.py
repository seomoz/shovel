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

'''Helpers for displaying help'''


import re
from shovel.tasks import Shovel


def heirarchical_helper(shovel, prefix, level=0):
    '''Return a list of tuples of (fullname, docstring, level) for all the
    tasks in the provided shovel'''
    result = []
    for key, value in sorted(shovel.map.items()):
        if prefix:
            key = prefix + '.' + key
        if isinstance(value, Shovel):
            result.append((key, None, level))
            result.extend(heirarchical_helper(value, key, level + 1))
        else:
            result.append((key, value.doc or '(No docstring)', level))
    return result


def heirarchical_help(shovel, prefix):
    '''Given a shovel of tasks, display a heirarchical list of the tasks'''
    result = []
    tuples = heirarchical_helper(shovel, prefix)
    if not tuples:
        return ''

    # We need to figure out the longest fullname length
    longest = max(len(name + '    ' * level) for name, _, level in tuples)
    fmt = '%%%is => %%-50s' % longest
    for name, docstring, level in tuples:
        if docstring == None:
            result.append('    ' * level + name + '/')
        else:
            docstring = re.sub(r'\s+', ' ', docstring).strip()
            if len(docstring) > 50:
                docstring = docstring[:47] + '...'
            result.append(fmt % (name, docstring))
    return '\n'.join(result)


def shovel_help(shovel, *names):
    '''Return a string about help with the tasks, or lists tasks available'''
    # If names are provided, and the name refers to a group of tasks, print out
    # the tasks and a brief docstring. Otherwise, just enumerate all the tasks
    # available
    if not len(names):
        return heirarchical_help(shovel, '')
    else:
        for name in names:
            task = shovel[name]
            if isinstance(task, Shovel):
                return heirarchical_help(task, name)
            else:
                return task.help()
