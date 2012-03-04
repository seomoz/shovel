from shovel import task

@task
def howdy(times=1):
    '''Just prints "Howdy" as many times as requests.
    
    Examples:
        shovel foo.howdy 10
        http://localhost:3000/foo.howdy?15'''
    print '\n'.join(['Howdy'] * int(times))