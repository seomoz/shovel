from shovel import task

@task
def hello(name='Foo'):
    '''Prints "Hello, " followed by the provided name.
    
    Examples:
        shovel bar.hello
        shovel bar.hello --name=Erin
        http://localhost:3000/bar.hello?Erin'''
    print 'Hello, %s' % name

@task
def args(*args):
    '''Echos back all the args you give it.
    
    This exists mostly to demonstrate the fact that shovel
    is compatible with variable argument functions.
    
    Examples:
        shovel bar.args 1 2 3 4
        http://localhost:3000/bar.args?1&2&3&4'''
    for arg in args:
        print 'You said "%s"' % arg

@task
def kwargs(**kwargs):
    '''Echos back all the kwargs you give it.
    
    This exists mostly to demonstrate that shovel is
    compatible with the keyword argument functions.
    
    Examples:
        shovel bar.kwargs --foo=5 --bar 5 --howdy hey
        http://localhost:3000/bar.kwargs?foo=5&bar=5&howdy=hey'''
    for key, val in kwargs.items():
        print 'You said "%s" => "%s"' % (key, val)