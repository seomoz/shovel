from shovel import task


@task
def bar():
    '''Dummy function'''
    print 'Hello from bar!'


@task
def foo():
    '''Dummy function'''
    print 'Hello from foo!'
