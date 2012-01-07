from shovel import task

@task
def hello(name):
    '''Prints hello and the provided name'''
    print 'Hello, %s!' % name

@task
def sumnum(*args):
    '''Computes the sum of the provided numbers'''
    print '%s = %f' % (' + '.join(args), sum(float(arg) for arg in args))

@task
def attributes(name, **kwargs):
    '''Prints a name, and all keyword attributes'''
    print '%s has attributes:' % name
    for key, value in kwargs.items():
        print '\t%s => %s' % (key, value)
