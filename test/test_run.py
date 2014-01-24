#! /usr/bin/env python

'''Ensure the `run` method works'''

import unittest

from contextlib import contextmanager
import logging
import os
from path import path
import shovel
import sys
try:
    from cStringIO import StringIO
except ImportError:  # pragma: no cover
    # Python 3 support
    from io import StringIO


@contextmanager
def capture(stream='stdout'):
    original = getattr(sys, stream)
    setattr(sys, stream, StringIO())
    yield(getattr(sys, stream))
    setattr(sys, stream, original)


@contextmanager
def logs():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    shovel.logger.addHandler(handler)
    yield(stream)
    handler.flush()
    shovel.logger.removeHandler(handler)


class TestRun(unittest.TestCase):
    '''Test our `run` method'''
    def stdout(self, pth, *args, **kwargs):
        with path(pth):
            with capture() as out:
                shovel.run(*args, **kwargs)
            return [line.strip() for line in
                out.getvalue().strip().split('\n')]

    def stderr(self, pth, *args, **kwargs):
        with path(pth):
            with capture('stderr') as out:
                shovel.run(*args, **kwargs)
            return [line.strip() for line in
                out.getvalue().strip().split('\n')]

    def logs(self, pth, *args, **kwargs):
        with path(pth):
            with logs() as out:
                shovel.run(*args, **kwargs)
            return [line.strip() for line in
                out.getvalue().strip().split('\n')]

    def test_basic(self):
        '''We should be able to run a command'''
        actual = self.stdout('test/examples/run/basic', 'bar')
        expected = [
            'Hello from bar!']
        self.assertEqual(actual, expected)

    def test_basic_help(self):
        '''Can run a basic example'''
        actual = self.stdout('test/examples/run/basic', 'help')
        expected = [
            'bar => Dummy function']
        self.assertEqual(actual, expected)

    def test_verbose(self):
        '''Can be run in verbose mode'''
        actual = self.logs('test/examples/run/basic', 'bar', '--verbose')
        # We have to replace absolue paths with relative ones
        actual = [line.replace(os.getcwd(), '') for line in actual]
        expected = [
            'Loading /test/examples/run/basic/shovel.py',
            'Found task bar in shovel']
        self.assertEqual(actual, expected)

    def test_task_missing(self):
        '''Exits if the task is missing'''
        self.assertRaises(
            SystemExit, self.stderr, 'test/examples/run/basic', 'whiz')

    def test_too_many_tasks(self):
        '''Exits if there are too many matching tasks'''
        self.assertRaisesRegexp(
            SystemExit, '2', self.stderr, 'test/examples/run/multiple', 'whiz')

    def test_dry_run(self):
        '''Honors the dry-run flag'''
        actual = self.stdout(
            'test/examples/run/basic', 'bar', '--dry-run')
        expected = ['Would have executed:', 'bar']
        self.assertEqual(actual, expected)

    def test_tasks(self):
        '''Make sure we can enumerate tasks'''
        actual = self.stdout(
            'test/examples/run/basic', 'tasks')
        expected = ['bar # Dummy function']
        self.assertEqual(actual, expected)

    def test_tasks_none_found(self):
        '''Display the correct thing when no tasks are found'''
        actual = self.stdout('test/examples/run/none', 'tasks')
        expected = ['No tasks found!']
        self.assertEqual(actual, expected)
