#!/usr/bin/env python

# Copyright (c) 2011 SEOmoz
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

import os
import logging
import inspect

logger = logging.getLogger('shovel')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# This is a global list of tasks that have been discovered
_tasks = {}
# This is a global list of the paths that we've discovered,
# and when they were last modified
_files = {}
base   = os.path.abspath('.')

# Make a task object for the provided object, and insert it into
# our global hash of known tasks
def task(f):
    Task.make(f)
    return f

class Args(object):
    # Takes a list of parsed values from argparse, and generates
    def __init__(self, spec):
        args = list(spec.args)
        args.reverse()
        
        defaults = list(spec.defaults or [])
        defaults.reverse()
        
        # Zip together the default arguments
        self._args = zip(args, defaults)
        # And get the remaining args, and append them with
        # no default argument args
        self._args.extend((arg) for arg in args[len(self._args):])
        self._args.reverse()
        # Now our internal args is a list of tuples of variable
        # names and their corresponding default values
        self._varargs = spec.varargs
        self._kwargs  = spec.keywords
        
        # While _args, _varargs, _kwargs are meant to be static, these
        # are meant to change depending when we're eval'd
        self.args    = list(self._args)
        self.varargs = []
        self.kwargs  = {}
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        output = []
        for pair in self.args:
            if isinstance(pair, tuple) and len(pair) == 2:
                output.append('%s=%s' % (pair[0], repr(pair[1])))
            else:
                output.append(pair)
        
        if self._varargs:
            output.append('%s=[%s]' % (self._varargs, ', '.join(repr(a) for a in self.varargs)))
        
        if self._kwargs:
            output.append('%s=%s' % (self._kwargs, repr(self.kwargs)))
        return '(' + ',\n\t'.join(output) + ')'
    
    def getArgs(self):
        '''Get a list and a hash that is representative of these args'''
        args  = []
        count = 0
        # At this point, self.args should be representative of the argument
        # as they should be supplied to the method
        for pair in self.args:
            if len(pair) < 2:
                total = len([a for a in self.args if len(a) == 1])
                raise ValueError('Argument %i not provided. Needs %i more' % (count, total))
            else:
                name, value = pair
                args.append(value)
                count += 1
        args.extend(self.varargs)
        return (args, self.kwargs)
    
    def eval(self, *args, **kwargs):
        '''Evaluate this argspec with the provided arguments'''
        self.args    = list(self._args)
        self.varargs = []
        for i in range(len(args)):
            if i < len(self.args):
                pair = self.args[i]
                self.args[i] = (pair[0], args[i])
            else:
                self.varargs.append(args[i])
        # For the remaining arguments, if there's a corresponding kwarg,
        # then we should insert is a positional arg.
        for i in range(len(args), len(self.args)):
            name = self.args[i][0]
            if name in kwargs:
                self.args[i] = (name, kwargs.pop(name))
        self.kwargs = kwargs

# First things first, we should have something that encapsulates a task
class Task(object):
    @classmethod
    def find(cls, fullname=''):
        mods = fullname.split('.')
        tasks = _tasks
        while len(mods) > 1:
            mod = mods.pop(0)
            if mod:
                tasks = tasks.get(mod, {})
        
        mod = mods.pop(0)
        if mod:
            remaining = tasks.get(mod, None)
            if not remaining:
                return []
            else:
                remaining = [remaining]
        else:
            remaining = [_tasks]
        
        # Alright. Now remaining is a list of dictionaries, or maybe
        # just a task. We should find all tasks under this module
        # and then return an array of found tasks
        found = []
        while len(remaining):
            next = remaining.pop(0)
            if isinstance(next, dict):
                remaining.extend(next.values())
            else:
                found.append(next)
        return found
    
    @classmethod
    def make(cls, obj):
        try:
            t = Task(obj)
            previous = Task.find(t.fullname)
            if previous:
                logger.warn('Task "%s" redefined' % t.fullname)
                logger.warn('\tPrevious definition in %s at %i' % (previous[0].file, previous[0].line))
                logger.warn('\tNew      definition in %s at %i' % (t.file, t.line))
            
            mods = t.fullname.split('.')
            tasks = _tasks
            while len(mods) > 1:
                mod = mods.pop(0)
                tasks.setdefault(mod, {})
                tasks = tasks[mod]
            
            tasks[mods.pop(0)] = t
        except Exception as e:
            logger.exception('Unable to make task for %s' % (repr(obj)))
    
    def __init__(self, obj):
        if not callable(obj):
            return
        
        self.name = obj.__name__
        self.doc  = inspect.getdoc(obj) or ''
        self.obj  = obj
        self.line = self.obj.__code__.co_firstlineno
        self.file = self.obj.__code__.co_filename
        self.module = self.obj.__module__
        
        global base
        path, sep, ext = os.path.relpath(self.file, base).rpartition('.py')
        if path == 'shovel':
            self.fullname = self.name
        else:
            mods = []
            base, name = os.path.split(path)
            while base:
                mods.append(name)
                base, name = os.path.split(base)
            if name != 'shovel':
                mods.append(name)
            mods.reverse()
            mods.append(self.name)
            self.fullname = '.'.join(mods)
        # If the provided object is a type (like a class), we'll treat
        # it a little differently from if it's a pure function. The 
        # assumption is that the class will be instantiated wit no 
        # arguments, and then called with the provided arguments
        if isinstance(obj, type):
            self.spec = inspect.getargspec(obj.__call__)
            self.type = 'class'
            self.doc  = inspect.getdoc(obj.__call__) or self.doc
        else:
            self.spec = inspect.getargspec(obj)
            self.type = 'function'
        
    def __call__(self, *args, **kwargs):
        '''Invoke the task itself'''
        if self.type == 'class':
            try:
                f = self.obj()
            except:
                raise TypeError('%s => Task classes must be instantiated without arguments' % self.name)
        else:
            f = self.obj
        
        # Now that we have a function, we should make an args object
        arg = Args(self.spec)
        arg.eval(*args, **kwargs)
        args, kwargs = arg.getArgs()
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception('Failed to run task %s' % self.name)
            raise(e)
    
    # This is a helper to allow us to run a task, and then get
    # back a dictionary of the various outputs -- stdout, stderr,
    # exceptions, return value
    def capture(self, *args, **kwargs):
        import sys
        import traceback
        from StringIO import StringIO
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = out = StringIO()
        sys.stderr = err = StringIO()
        result = {
            'exception': None,
            'stderr'   : None,
            'stdout'   : None,
            'return'   : None
        }
        try:
            result['return'] = repr(self.__call__(*args, **kwargs))
        except:
            result['exception'] = traceback.format_exc()
        sys.stdout, sys.stderr = stdout, stderr
        result['stderr'] = err.getvalue()
        result['stdout'] = out.getvalue()
        return result
    
    def dry(self, *args, **kwargs):
        '''Perform a dry-run of the task'''
        arg = Args(self.spec)
        arg.eval(*args, **kwargs)
        return 'Would have executed:\n%s%s' % (self.name, repr(arg))
    
    def help(self):
        # Return the help for this function
        s = '=' * 50 + '\n'
        s += self.name + '\n'
                
        # And the doc, if it exists
        if self.doc:
            s += '=' * 30 + '\n'
            s += self.doc + '\n'
        
        # Print where we read this function in from
        s += '=' * 30 + '\n'
        s += 'From %s on line %i\n' % (self.file, self.line)
        
        # And finally how it's invoked
        args = Args(self.spec)
        s += '=' * 30 + '\n'
        s += '%s%s\n' % (self.name, repr(args))
        return s

def help_helper(tasks):
    import re
    # This returns a nice, pretty representation of the tasks' help
    s = ''
    modules = []
    for task in tasks:
        # Get the module names for the task
        m = task.fullname.split('.')
        name = m.pop()
        # If there are multiple layers here, then we should
        # print a heirarchical structure.
        unmatched = []
        for i in range(len(m)):
            if i >= len(modules):
                unmatched = m[i:]
                break
            elif modules[i] != m[i]:
                unmatched = m[i:]
                modules = modules[:i]
                break
        for module in unmatched:
            s += '\t' * len(modules) + module + '/\n'
            modules.append(module)
        
        if len(task.doc) > 50:
            s += '%30s => %s...\n' % (task.fullname, re.sub(r'\s+', ' ', task.doc)[0:47])
        else:
            s += '%30s => %s\n' % (task.fullname, re.sub(r'\s+', ' ', task.doc))
    return s

def help(*names):
    '''Display information about the provided task name, or available tasks'''
    if not len(names):
        print help_helper(Task.find())
    else:
        for name in names:
            tasks = Task.find(name)
            if not tasks:
                print 'Could not find task or module "%s"' % name
            elif len(tasks) == 1:
                print tasks[0].help()
            else:
                print help_helper(tasks)

def load():
    '''Load tasks from files'''
    import os
    import re
    import sys
    import imp
    import time
    p = os.path.abspath('./shovel.py')
    if os.path.isfile(p) and _files.get(p, 0) < os.stat(p).st_mtime:
        with file(p) as f:
            logger.info('Loading %s' % p)
            r = imp.find_module('shovel', ['.'])
            module = imp.load_module('shovel', r[0], r[1], r[2])
            _files[p] = os.stat(p).st_mtime
    elif os.path.isdir(os.path.abspath('./shovel')):
        for root, dirs, files in os.walk(os.path.abspath('./shovel')):
            for name in [f for f in files if re.match(r'.+\.py$', f)]:
                p = os.path.join(root, name)
                if _files.get(p, 0) < os.stat(p).st_mtime:
                    logger.info('Loading %s' % p)
                    name, sep, ext = name.rpartition('.py')
                    r = imp.find_module(name, [root])
                    module = imp.load_module(name, r[0], r[1], r[2])
                    _files[p] = os.stat(p).st_mtime
