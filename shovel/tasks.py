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

'''Task helper'''

import os
import imp
import sys
import inspect
from collections import defaultdict

# Internal imports
from shovel import logger
from shovel.args import Args


def task(func):
    '''Register this task with shovel, but return the original function'''
    Task.make(func)
    return func


class Shovel(object):
    '''A collection of tasks contained in a file or folder'''
    @classmethod
    def load(cls, path, base=None):
        '''Either load a path and return a shovel object or return None'''
        obj = cls()
        obj.read(path, base)
        return obj

    def __init__(self, tasks=None):
        self.overrides = None
        self._tasks = tasks or []
        self.map = defaultdict(Shovel)
        self.extend(tasks or [])

    def extend(self, tasks):
        '''Add tasks to this particular shovel'''
        self._tasks.extend(tasks)
        for task in tasks:
            # We'll now go through all of our tasks and group them into
            # sub-shovels
            current = self.map
            modules = task.fullname.split('.')
            for module in modules[:-1]:
                if not isinstance(current[module], Shovel):
                    logger.warn('Overriding task %s with a module' %
                        current[module].file)
                    shovel = Shovel()
                    shovel.overrides = current[module]
                    current[module] = shovel
                current = current[module].map

            # Now we'll put the task in this particular sub-shovel
            name = modules[-1]
            if name in current:
                logger.warn('Overriding %s with %s' % (
                    '.'.join(modules), task.file))
                task.overrides = current[name]
            current[name] = task

    def read(self, path, base=None):
        '''Import some tasks'''
        if base == None:
            base = os.getcwd()
        absolute = os.path.abspath(path)
        if os.path.isfile(absolute):
            # Load that particular file
            logger.info('Loading %s' % absolute)
            self.extend(Task.load(path, base))
        elif os.path.isdir(absolute):
            # Walk this directory looking for tasks
            tasks = []
            for root, _, files in os.walk(absolute):
                files = [f for f in files if f.endswith('.py')]
                for child in files:
                    absolute = os.path.join(root, child)
                    logger.info('Loading %s' % absolute)
                    tasks.extend(Task.load(absolute, base))
            self.extend(tasks)

    def __getitem__(self, key):
        '''Find a task with the provided name'''
        current = self.map
        split = key.split('.')
        for module in split[:-1]:
            if module not in current:
                raise KeyError('Module not found')
            current = current[module].map
        if split[-1] not in current:
            raise KeyError('Task not found')
        return current[split[-1]]

    def __contains__(self, key):
        try:
            return bool(self.__getitem__(key))
        except KeyError:
            return False

    def keys(self):
        '''Return all valid keys'''
        keys = []
        for key, value in self.map.items():
            if isinstance(value, Shovel):
                keys.extend([key + '.' + k for k in value.keys()])
            else:
                keys.append(key)
        return sorted(keys)

    def items(self):
        '''Return a list of tuples of all the keys and tasks'''
        pairs = []
        for key, value in self.map.items():
            if isinstance(value, Shovel):
                pairs.extend([(key + '.' + k, v) for k, v in value.items()])
            else:
                pairs.append((key, value))
        return sorted(pairs)

    def tasks(self, name):
        '''Get all the tasks that match a name'''
        found = self[name]
        if isinstance(found, Shovel):
            return [v for _, v in found.items()]
        return [found]


class Task(object):
    '''An object representative of a task'''
    # There's an interesting problem associated with this process of loading
    # tasks from a file. We invoke it with a 'load', but then we get access to
    # the tasks through decorators. As such, the decorator just accumulates
    # the tasks that it has seen as it creates them, puts them in a cache, and
    # eventually that cache will be consumed as a usable object. This is that
    # cache. Put another way:
    #
    #   1. Clear cache
    #   2. Load module
    #   3. Fill cache with tasks created with @task
    #   4. Once loaded, organize the cached tasks
    _cache = []
    # This is to help find tasks given their path
    _tasks = {}

    @classmethod
    def make(cls, obj):
        '''Given a callable object, return a new callable object'''
        try:
            cls._cache.append(Task(obj))
        except Exception:
            logger.exception('Unable to make task for %s' % repr(obj))

    @classmethod
    def load(cls, path, base=None):
        '''Return a list of the tasks stored in a file'''
        base = base or os.getcwd()
        absolute = os.path.abspath(path)
        parent = os.path.dirname(absolute)
        name, _, _ = os.path.basename(absolute).rpartition('.py')
        fobj, path, description = imp.find_module(name, [parent])
        try:
            imp.load_module(name, fobj, path, description)
        finally:
            if fobj:
                fobj.close()
        # Manipulate the full names of the tasks to be relative to the provided
        # base
        relative, _, _ = os.path.relpath(path, base).rpartition('.py')
        for task in cls._cache:
            parts = relative.split(os.path.sep)
            parts.append(task.name)
            # If it's either in shovel.py, or folder/__init__.py, then we
            # should consider it as being at one level above that file
            parts = [part.strip('.') for part in parts if part not in
                ('shovel', '.shovel', '__init__', '.', '..', '')]
            task.fullname = '.'.join(parts)
            logger.debug('Found task %s in %s' % (task.fullname, task.module))
        return cls.clear()

    @classmethod
    def clear(cls):
        '''Clear and return the cache'''
        cached = cls._cache
        cls._cache = []
        return cached

    def __init__(self, obj):
        if not callable(obj):
            raise TypeError('Object not callable: %s' % obj)

        # Save some attributes about the task
        self.name = obj.__name__
        self.doc = inspect.getdoc(obj) or ''

        # If the provided object is a type (like a class), we'll treat
        # it a little differently from if it's a pure function. The
        # assumption is that the class will be instantiated wit no
        # arguments, and then called with the provided arguments
        if isinstance(obj, type):
            try:
                self._obj = obj()
            except:
                raise TypeError(
                    '%s => Task classes must take no arguments' % self.name)
            self.spec = inspect.getargspec(self._obj.__call__)
            self.doc = inspect.getdoc(self._obj.__call__) or self.doc
            self.line = 'Unknown line'
            self.file = 'Unknown file'
        else:
            self.spec = inspect.getargspec(obj)
            self._obj = obj
            self.line = obj.__code__.co_firstlineno
            self.file = obj.__code__.co_filename

        self.module = self._obj.__module__
        self.fullname = self.name

        # What module / etc. this overrides, if any
        self.overrides = None

    def __call__(self, *args, **kwargs):
        '''Invoke the task itself'''
        try:
            return self._obj(*args, **kwargs)
        except Exception as exc:
            logger.exception('Failed to run task %s' % self.name)
            raise(exc)

    def capture(self, *args, **kwargs):
        '''Run a task and return a dictionary with stderr, stdout and the
        return value. Also, the traceback from the exception if there was
        one'''
        import traceback
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = out = StringIO()
        sys.stderr = err = StringIO()
        result = {
            'exception': None,
            'stderr': None,
            'stdout': None,
            'return': None
        }
        try:
            result['return'] = self.__call__(*args, **kwargs)
        except Exception:
            result['exception'] = traceback.format_exc()
        sys.stdout, sys.stderr = stdout, stderr
        result['stderr'] = err.getvalue()
        result['stdout'] = out.getvalue()
        return result

    def dry(self, *args, **kwargs):
        '''Perform a dry-run of the task'''
        return 'Would have executed:\n%s%s' % (
            self.name, Args(self.spec).explain(*args, **kwargs))

    def help(self):
        '''Return the help string of the task'''
        # This returns a help string for a given task of the form:
        #
        # ==================================================
        # <name>
        # ============================== (If supplied)
        # <docstring>
        # ============================== (If overrides other tasks)
        # Overrides <other task file>
        # ==============================
        # From <file> on <line>
        # ==============================
        # <name>(Argspec)
        result = [
            '=' * 50,
            self.name
        ]

        # And the doc, if it exists
        if self.doc:
            result.extend([
                '=' * 30,
                self.doc
            ])

        override = self.overrides
        while override:
            if isinstance(override, Shovel):
                result.append('Overrides module')
            else:
                result.append('Overrides %s' % override.file)
            override = override.overrides

        # Print where we read this function in from
        result.extend([
            '=' * 30,
            'From %s on line %i' % (self.file, self.line),
            '=' * 30,
            '%s%s' % (self.name, str(Args(self.spec)))
        ])
        return os.linesep.join(result)
