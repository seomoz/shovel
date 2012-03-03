from shovel import task

@task
def howdy(times=1):
    '''Just prints "Howdy" as many times as requests'''
    print '\n'.join(['Howdy'] * int(times))