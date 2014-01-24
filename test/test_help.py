#! /usr/bin/env python

'''Ensure our help messages work'''

import unittest

import os
from shovel import help
from shovel.tasks import Shovel


class TestHelp(unittest.TestCase):
    '''Make sure our help messages work'''
    def setUp(self):
        self.shovel = Shovel.load(
            'test/examples/help/', 'test/examples/help/')

    def test_heirarchical_helper(self):
        '''Gets all the help tuples we'd expect'''
        expected = [
            ('one', None, 0),
            ('one.widget', 'A dummy function', 1),
            ('two', None, 0),
            ('two.widget', 'long doc, ' * 7, 1)]
        self.assertEqual(help.heirarchical_helper(self.shovel, ''), expected)

    def test_heirarchical_help(self):
        '''Gets the help message we'd expect from heirarchical_help'''
        actual = [line.strip() for line in
            help.heirarchical_help(self.shovel, '').split('\n')]
        expected = [
            'one/',
            'one.widget => A dummy function',
            'two/',
            'two.widget => long doc, long doc, long doc, long doc, long do...']
        self.assertEqual(actual, expected)

    def test_shovel_help_basic(self):
        '''Gets the help message we'd expect from shovel_help for all tasks'''
        actual = [line.strip() for line in
            help.shovel_help(self.shovel).split('\n')]
        expected = [
            'one/',
            'one.widget => A dummy function',
            'two/',
            'two.widget => long doc, long doc, long doc, long doc, long do...']
        self.assertEqual(actual, expected)

    def test_shovel_help_specific_tasks(self):
        '''Gets the help message we'd expect from shovel_help for tasks'''
        actual = [line.strip() for line in
            help.shovel_help(self.shovel, 'two').split('\n')]
        expected = [
            'two.widget => long doc, long doc, long doc, long doc, long do...']
        self.assertEqual(actual, expected)

    def test_shovel_help_specific_task(self):
        '''Gets the help message we'd expect from shovel_help for a task'''
        actual = [line.strip() for line in
            help.shovel_help(self.shovel, 'two.widget').split('\n')]
        # We need to replace absolute paths in the test
        actual = [line.replace(os.getcwd(), '') for line in actual]
        expected = [
            '==================================================',
            'widget',
            '==============================',
            ('long doc, ' * 7).strip(),
            '==============================',
            'From /test/examples/help/two.py on line 6',
            '==============================',
            'widget()']
        self.assertEqual(actual, expected)

    def test_help_missing_docstring(self):
        '''We should print '(No docstring)' for tasks missing a docstring'''
        shovel = Shovel.load(
            'test/examples/docstring/', 'test/examples/docstring/')
        actual = [line.strip() for line in help.shovel_help(shovel).split('\n')]
        expected = ['one/', 'one.foo => (No docstring)']
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
