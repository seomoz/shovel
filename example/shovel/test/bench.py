from shovel import task

@task
def data():
    '''This might run some test benchmark.
    
    Examples:
        shovel test.bench.data
        http://localhost:3000/test.bench.data'''
    return {
        'average': 5,
        'total'  : 7,
        'count'  : 100
    }
