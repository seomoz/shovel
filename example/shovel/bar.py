from shovel import task

@task
def hello(name='Foo'):
    '''Prints "Hello, " followed by the provided name'''
    print 'Hello, %s' % name

@task
def args(*args):
    '''Echos back all the args you give it'''
    for arg in args:
        print 'You said "%s"' % arg

@task
def kwargs(**kwargs):
    '''Echos back all the kwargs you give it'''
    for key, val in kwargs.items():
        print 'You said "%s" => "%s"' % (key, val)