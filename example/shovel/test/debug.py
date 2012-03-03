from shovel import task

@task
def verbose():
    '''Maybe this runs some very verbose output'''
    print 'Good news, everyone!\n' * 100

@task
def something(a, b, c):
    '''Another kind of debugging'''
    raise Exception('Something broke')
    