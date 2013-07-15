from shovel import task


@task
class Foo(object):
    '''This class cannot be a shovel-style functor'''
    def __init__(self, foo):
        self.foo = foo

    def __call__(self, foo):
        return foo
