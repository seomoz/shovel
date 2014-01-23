'''Shovel tasks strictly for tests'''

from shovel import task


@task
def widget(arg, whiz, bang):
    '''This is a dummy task'''
    return arg + whiz + bang
