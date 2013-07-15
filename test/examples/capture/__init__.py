from shovel import task

@task
def foo(a, b, c):
    '''Dummy function'''
    print 'foo'
    return a + b + c


@task
def bar():
    '''Dummy function'''
    raise TypeError('Doh')
