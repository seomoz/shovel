#!/usr/bin/env python

import os
import logging
import inspect

logger = logging.getLogger('shovel')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# This is a global list of tasks that have been discovered
_tasks = {}
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
            if len(pair) == 2:
                output.append('%s=%s' % (pair[0], repr(pair[1])))
            else:
                output.append(pair[0])
        
        if self._varargs:
            output.append('%s=[%s]' % (self._varargs, ', '.join(repr(a) for a in self.varargs)))
        
        if self._kwargs:
            output.append('%s=%s' % (self._kwargs, repr(self.kwargs)))
        return '(' + ',\n\t'.join(output) + ')'
    
    def getArgs(self):
        '''Get a list and a hash that is representative of these args'''
        args  = []
        count = 0
        for pair in self.args:
            if len(pair) < 2:
                total = len([a for a in self.args if len(a) == 1])
                raise ValueError('Argument %i not provided. Needs %i more' % (count, total))
            else:
                count += 1
                args.append(pair[1])
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
        self.kwargs = kwargs

# First things first, we should have something that encapsulates a task
class Task(object):
    @classmethod
    def all(cls, base=_tasks):
        tasks = []
        toprocess = [base]
        while len(toprocess):
            next = toprocess.pop(0)
            for key, value in next.items():
                if isinstance(value, dict):
                    toprocess.append(value)
                else:
                    tasks.append(value)
        return tasks
    
    @classmethod
    def find(cls, fullname):
        mods = fullname.split('.')
        tasks = _tasks
        while len(mods) > 1:
            tasks = tasks.get(mods.pop(0), {})
        return tasks.get(mods.pop(0), None)
    
    @classmethod
    def make(cls, obj):
        try:
            t = Task(obj)
            previous = Task.find(t.fullname)
            if previous:
                logger.warn('Task "%s" redefined' % t.name)
                logger.warn('\tPrevious definition in %s.%s at %i' % (t.module, t.file, t.line))
                logger.warn('\tNew      definition in %s.%s at %i' % (t.module, t.file, t.line))
            
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
            f(*args, **kwargs)
        except Exception as e:
            logger.exception('Failed to run task %s' % self.name)
    
    def dry(self, *args, **kwargs):
        '''Perform a dry-run of the task'''
        arg = Args(self.spec)
        arg.eval(*args, **kwargs)
        print '%s%s' % (self.name, repr(arg))
    
    def help(self):
        # Print the name of the function
        print '=' * 50
        print self.name
                
        # And the doc, if it exists
        if self.doc:
            print '=' * 30
            print self.doc
        
        # Print where we read this function in from
        print '=' * 30
        print 'From %s.%s on line %i' % (self.module, self.file, self.line)
        
        # And finally how it's invoked
        args = Args(self.spec)
        print '=' * 30
        print '%s%s' % (self.name, repr(args))

def help(*names):
    '''Display information about the provided task name, or available tasks'''
    if not len(names):
        for task in Task.all():
            if len(task.doc) > 50:
                print '%30s => %47s...' % (task.fullname, task.doc[0:47])
            else:
                print '%30s => %50s' % (task.fullname, task.doc)
    else:
        for name in names:
            t = Task.find(name)
            if t == None:
                print 'Could not find task or module "%s"' % name
            elif isinstance(t, dict):
                for task in Task.all(t):
                    if len(task.doc) > 50:
                        print '%30s => %47s...' % (task.fullname, task.doc[0:47])
                    else:
                        print '%30s => %50s' % (task.fullname, task.doc)
            else:
                t.help()

def load():
    '''Load tasks from files'''
    import re
    import sys
    p = os.path.abspath('./shovel.py')
    if os.path.isfile(p):
        with file(p) as f:
            code = compile(f.read(), p, 'exec')
            exec code
    elif os.path.isdir(os.path.abspath('./shovel')):
        for root, dirs, files in os.walk(os.path.abspath('./shovel')):
            if root not in sys.path:
                sys.path.append(root)
            for name in [f for f in files if re.match(r'.+\.py$', f)]:
                print 'Found python file %s' % os.path.join(root, name)
                #name, sep, ext = name.rpartition('.py')
                p = os.path.join(root, name)
                with file(p) as f:
                    code = compile(f.read(), p, 'exec')
                    exec code

