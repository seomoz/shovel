#! /usr/bin/env python

'''Ensure that we can correctly find tasks'''

import unittest
from shovel.tasks import Shovel, Task


class TestTask(unittest.TestCase):
    '''Test our ability to find and correctly reference tasks'''
    def test_basic(self):
        '''Ensure that we can get all the basic tasks in a shovel file'''
        shovel = Shovel.load('test/examples/basic/shovel.py',
            'test/examples/basic')
        self.assertNotEqual(shovel, None)
        self.assertTrue('widget' in shovel)

    def test_folder(self):
        '''Ensure we can import from a folder structure'''
        shovel = Shovel.load('test/examples/folder/', 'test/examples/folder/')
        self.assertNotEqual(shovel, None)
        self.assertTrue('foo.widget' in shovel)

    def test_init(self):
        '''Ensure we can recognize things in __init__ correctly'''
        shovel = Shovel.load('test/examples/init/', 'test/examples/init/')
        self.assertNotEqual(shovel, None)
        self.assertTrue('widget' in shovel)

    def test_nested(self):
        '''Ensure we can do nested loading'''
        shovel = Shovel.load('test/examples/nested/', 'test/examples/nested/')
        self.assertNotEqual(shovel, None)
        examples = [
            'foo.bar',
            'foo.whiz',
            'foo.baz.hello',
            'foo.baz.howdy.what'
        ]
        for example in examples:
            self.assertTrue(example in shovel)

    def test_override(self):
        '''Ensure we can track overrides from one file or another'''
        shovel = Shovel()
        for name in ['one', 'two']:
            pth = 'test/examples/overrides/%s' % name
            shovel.read(pth, pth)
        self.assertNotEqual(shovel, None)
        self.assertNotEqual(shovel['foo.bar'].overrides, None)

    def test_keys_items(self):
        '''Shovels should provide a list of all the tasks they know about'''
        shovel = Shovel.load('test/examples/nested/', 'test/examples/nested/')
        keys = [
            'foo.bar',
            'foo.whiz',
            'foo.baz.hello',
            'foo.baz.howdy.what'
        ]
        self.assertEqual(set(shovel.keys()), set(keys))
        for key, pair in zip(sorted(keys), sorted(shovel.items())):
            self.assertEqual(key, pair[0])
            self.assertEqual(key, pair[1].fullname)

    def test_multi_load(self):
        '''Load from multiple paths'''
        shovel = Shovel()
        shovel.read('test/examples/multiple/one/',
            'test/examples/multiple/one/')
        shovel.read('test/examples/multiple/two/',
            'test/examples/multiple/two/')
        keys = [
            'whiz', 'bar.bar'
        ]
        self.assertEqual(set(shovel.keys()), set(keys))

    def test_errors(self):
        '''Make sure getting non-existant tasks throws errors'''
        shovel = Shovel()
        self.assertRaises(KeyError, shovel.__getitem__, 'foo.bar.whiz')
        self.assertRaises(KeyError, shovel.__getitem__, 'foo')
        self.assertFalse('foo' in shovel)

        # We can't have functor classes that take arguments
        shovel.read('test/examples/errors/')
        self.assertFalse('Foo' in shovel)

        self.assertRaises(TypeError, Task, 'foo')

    def test_classes(self):
        '''We should be able to also use functor classes'''
        shovel = Shovel.load('test/examples/classes', 'test/examples/classes')
        self.assertTrue('Foo' in shovel)
        self.assertEqual(shovel['Foo'](5), 5)
        self.assertRaises(TypeError, shovel['Bar'], 5)

    def test_capture(self):
        '''Make sure we can capture output from a function'''
        shovel = Shovel.load('test/examples/capture/', 'test/examples/capture')
        self.assertEqual(shovel['foo'].capture(1, 2, 3), {
            'stderr': '',
            'stdout': 'foo\n',
            'return': 6,
            'exception': None
        })
        self.assertNotEqual(shovel['bar'].capture()['exception'], None)

    def test_atts(self):
        '''Make sure some of the attributes are what we expect'''
        shovel = Shovel.load('test/examples/capture/', 'test/examples/capture')
        task = shovel['foo']
        self.assertEqual(task.doc, 'Dummy function')

    def test_tasks(self):
        '''We should be able to get a list of all tasks that match a path'''
        shovel = Shovel.load('test/examples/tasks/', 'test/examples/tasks/')
        self.assertEqual(set(t.fullname for t in shovel.tasks('foo')),
            set(('foo.bar', 'foo.whiz')))

    def test_help(self):
        '''Just make sure that help doesn't blow up on us'''
        shovel = Shovel.load('test/examples/overrides/',
            'test/examples/overrides/')
        _, tasks = zip(*shovel.items())
        self.assertGreater(len(tasks), 0)
        for task in tasks:
            self.assertNotEqual(task.help(), '')

    def test_dry_run(self):
        '''Make sure that dry runs don't blow up on us'''
        shovel = Shovel.load('test/examples/multiple/',
            'test/examples/multiple/')
        _, tasks = zip(*shovel.items())
        self.assertGreater(len(tasks), 0)
        for task in tasks:
            self.assertNotEqual(task.dry(), '')

    def test_shovel(self):
        '''For shovel/*, shovel.py, .shovel/* and .shovel.py, tasks should be
        top-level'''
        shovel = Shovel.load('test/examples/toplevel/one',
            'test/examples/toplevel/one')
        _, tasks = zip(*shovel.items())
        # self.assertEqual(len(tasks), 4)
        self.assertEqual(set([t.fullname for t in tasks]),
            set(['whiz', 'bang']))

        shovel = Shovel.load('test/examples/toplevel/two',
            'test/examples/toplevel/two')
        _, tasks = zip(*shovel.items())
        self.assertEqual(set([t.fullname for t in tasks]),
            set(['foo', 'bar']))

if __name__ == '__main__':
    unittest.main()
