from shovel import task

@task
def data():
    '''This might run some test benchmark'''
    return {
        'average': 5,
        'total'  : 7,
        'count'  : 100
    }
