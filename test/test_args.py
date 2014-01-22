#! /usr/bin/env python

'''Ensure our args utilities work'''

import unittest
from shovel.args import Args


class TestArgs(unittest.TestCase):
    '''Test our argspec wrapper'''
    def test_basic(self):
        '''Give it a low-ball function'''
        def foo(a, b, c):
            pass

        args = Args.parse(foo)
        self.assertEqual(args.get(1, 2, 3).required, [
            ('a', 1), ('b', 2), ('c', 3)])
        self.assertEqual(args.get(1, 2, c=3).required, [
            ('a', 1), ('b', 2)])

    def test_default(self):
        '''We should be able to figure out defaults and overrides'''
        def foo(a, b, c=3, d=6):
            pass

        args = Args.parse(foo)
        self.assertEqual(args.get(1, 2).defaulted, [
            ('c', 3), ('d', 6)])
        self.assertEqual(args.get(1, 2, 4).defaulted, [
            ('d', 6)])
        self.assertEqual(args.get(1, 2, 4).overridden, [
            ('c', 4)])
        self.assertEqual(args.get(1, 2, c=4).defaulted, [
            ('d', 6)])

    def test_varargs(self):
        '''Oh, and varargs'''
        def foo(a, b, c=3, *d):
            pass

        args = Args.parse(foo)
        self.assertEqual(args.get(1, 2).varargs, ())
        self.assertEqual(args.get(1, 2, 3).varargs, ())
        self.assertEqual(args.get(1, 2, 3, 4, 5).varargs, (4, 5))

    def test_kwargs(self):
        '''We should also be able to use kwargs'''
        def foo(a, b, c=3, *d, **kwargs):
            pass

        args = Args.parse(foo)
        self.assertEqual(args.get(1, 2).kwargs, {})
        self.assertEqual(args.get(1, 2, 3).kwargs, {})
        self.assertEqual(args.get(1, 2, 3, 4, 5).kwargs, {})
        self.assertEqual(args.get(1, 2, 3, 4, 5, c=3, g=4).kwargs, {
            'c': 3, 'g': 4
        })

    def test_error(self):
        '''Giving too many or too few args should raise an error'''
        def foo(a, b, c):
            pass

        args = Args.parse(foo)
        self.assertRaises(Exception, args.get, 1, 2)
        self.assertRaises(Exception, args.get, 1, 2, 3, 4)

    def test_str_basic(self):
        '''Gets a representation of a basic function'''
        def foo(a, b=2):
            pass

        self.assertEqual(str(Args.parse(foo)), '(a, b=2)')

    def test_str_complex(self):
        '''Gets a representation of a more complex function'''
        def foo(a, b=2, *args, **kwargs):
            pass

        self.assertEqual(str(Args.parse(foo)), '(a, b=2, *args, **kwargs)')

    def test_explain(self):
        '''Gets a description of how arguments are applied'''
        def foo(a, b=2, *args, **kwargs):
            pass

        actual = [line.strip() for line in
            Args.parse(foo).explain(5, 3, 15, bar=20).split('\n')]
        expected = [
            'a = 5',
            'b = 3 (overridden)',
            'args = (15,)',
            'kwargs = {\'bar\': 20}']
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
