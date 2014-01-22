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

'''Helping functions for parsing CLI interface stuff'''


def parse(tokens):
    '''Parse the provided string to produce *args and **kwargs'''
    args = []
    kwargs = {}
    last = None
    for token in tokens:
        if token.startswith('--'):
            # If this is a keyword flag, but we've already got one that we've
            # parsed, then we're going to interpret it as a bool
            if last:
                kwargs[last] = True
            # See if it is the --foo=5 style
            last, _, value = token.strip('-').partition('=')
            if value:
                kwargs[last] = value
                last = None
        elif last != None:
            kwargs[last] = token
            last = None
        else:
            args.append(token)

    # If there's a dangling last, set that bool
    if last:
        kwargs[last] = True

    return args, kwargs
