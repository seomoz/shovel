from shovel import task

@task
def verbose():
    '''This just prints "Good news, everyone" 100 times.
    
    Examples:
    shovel test.debug.verbose
    http://localhost:3000/test.debug.verbose'''
    print('Good news, everyone!\n' * 100)

@task
def difference(a, b):
    '''Returns the difference between a and b, but only if a >= b.
    If a < b, then it raises an exception.
    
    Examples:
    shovel test.debug.difference 5 2
    shovel test.debug.difference 2 5
    http://localhost:3000/test.debug.difference?5&2 
    http://localhost:3000/test.debug.difference?a=2&b=5'''
    if int(a) < int(b):
        raise Exception('a must be greater than or equal to than b')
    else:
        return int(a) - int(b)

@task
def faily(*args, **kwargs):
    '''This always throws an exception, no matter what args you provide.
    
    Examples:
    shovel test.debug.faily
    http://localhost:3000/test.debug.faily'''
    raise Exception('I always fail!')