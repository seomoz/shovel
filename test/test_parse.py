#! /usr/bin/env python

'''Ensure our CLI parsing works'''

import unittest
from shovel.parser import parse


class TestParse(unittest.TestCase):
    '''Test our argspec wrapper'''
    def test_basic(self):
        '''A few low-ball examples'''
        args, kwargs = parse('1 2 3 4 5'.split(' '))
        self.assertEqual(args, ['1', '2', '3', '4', '5'])
        self.assertEqual(kwargs, {})

        # Make sure we handle bool flags
        args, kwargs = parse('--foo --bar --whiz'.split(' '))
        self.assertEqual(args, [])
        self.assertEqual(kwargs, {'foo': True, 'bar': True, 'whiz': True})

        # Make sure we can handle interleaved positional and keyword args
        args, kwargs = parse('1 --foo 5 2 3'.split(' '))
        self.assertEqual(args, ['1', '2', '3'])
        self.assertEqual(kwargs, {'foo': '5'})

        # Make sure we can handle '--foo=6'
        args, kwargs = parse('1 --foo=5'.split(' '))
        self.assertEqual(args, ['1'])
        self.assertEqual(kwargs, {'foo': '5'})


if __name__ == '__main__':
    unittest.main()
