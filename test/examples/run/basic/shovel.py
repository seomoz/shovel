'''Dummy shovel tasks for testing'''

from __future__ import print_function

from shovel import task


@task
def bar():
    '''Dummy function'''
    print('Hello from bar!')
