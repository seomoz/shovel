from shovel import task

@task
class Foo(object):
    ''''Functor class'''
    def __call__(self, foo):
        return foo


@task
class Bar(object):
    '''Functor class'''
    def __call__(self, foo):
        raise TypeError(foo)
