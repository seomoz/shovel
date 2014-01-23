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

'''Argument -parsing and -evaluating tools'''

from __future__ import print_function

import inspect
from collections import namedtuple


ArgTuple = namedtuple('ArgTuple',
    ('required', 'overridden', 'defaulted', 'varargs', 'kwargs'))


class Args(object):
    '''Represents an argspec, and evaluates provided arguments to complete an
    invocation. It wraps an `argspec`, and provides some utility functionality
    around actually evaluating args and kwargs given that argspec.'''
    @classmethod
    def parse(cls, obj):
        '''Get the Args object associated with the argspec'''
        return cls(inspect.getargspec(obj))

    def __init__(self, spec):
        # We need to keep track of all our arguments and their defaults. Since
        # defaults are provided from the tail end of the positional args, we'll
        # reverse those and the defaults from the argspec and pair them. Then
        # we'll add the required positional arguments and get a list of all
        # args and whether or not they have defaults
        self._defaults = list(reversed(
            list(zip(reversed(spec.args or []), reversed(spec.defaults or [])))
        ))
        # Now, take all the args that don't have a default
        self._args = spec.args[:(len(spec.args) - len(self._defaults))]
        # Now our internal args is a list of tuples of variable
        # names and their corresponding default values
        self._varargs = spec.varargs
        self._kwargs = spec.keywords

    def __str__(self):
        results = []
        results.extend(self._args)
        results.extend('%s=%s' % (k, v) for k, v in self._defaults)
        if self._varargs:
            results.append('*%s' % self._varargs)
        if self._kwargs:
            results.append('**%s' % self._kwargs)
        return '(' + ', '.join(results) + ')'

    def explain(self, *args, **kwargs):
        '''Return a string that describes how these args are interpreted'''
        args = self.get(*args, **kwargs)
        results = ['%s = %s' % (name, value) for name, value in args.required]
        results.extend(['%s = %s (overridden)' % (
            name, value) for name, value in args.overridden])
        results.extend(['%s = %s (default)' % (
            name, value) for name, value in args.defaulted])
        if self._varargs:
            results.append('%s = %s' % (self._varargs, args.varargs))
        if self._kwargs:
            results.append('%s = %s' % (self._kwargs, args.kwargs))
        return '\n\t'.join(results)

    def get(self, *args, **kwargs):
        '''Evaluate this argspec with the provided arguments'''
        # We'll go through all of our required args and make sure they're
        # present
        required = [arg for arg in self._args if arg not in kwargs]
        if len(args) < len(required):
            raise TypeError('Missing arguments %s' % required[len(args):])
        required = list(zip(required, args))
        args = args[len(required):]

        # Now we'll look through our defaults, if there are any
        defaulted = [(name, default) for name, default in self._defaults
            if name not in kwargs]
        overridden = list(zip([d[0] for d in defaulted], args))
        args = args[len(overridden):]
        defaulted = defaulted[len(overridden):]

        # And anything left over is in varargs
        if args and not self._varargs:
            raise TypeError('Too many arguments provided')

        return ArgTuple(required, overridden, defaulted, args, kwargs)
