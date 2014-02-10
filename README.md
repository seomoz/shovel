Shovel
======
[![Build Status](https://travis-ci.org/seomoz/shovel.png?branch=travis)](https://travis-ci.org/seomoz/shovel)

Shovel is like Rake for python. Turn python functions into tasks simply, and 
access and invoke them from the command line. 'Nuff said. __New__ Shovel also
now has support for invoking the same tasks in the browser you'd normally run
from the command line, without any modification to your shovel scripts.

Philosophy of Shovel
--------------------

- __Tasks should be easy to define__ -- one decorator, no options
- __Turning a function into task should change as little as possible__ -- 
	we don't want you to have to change the function's interface at all
- __Arguments are strings__ -- rather than guess about the type of input
	parameters, we're just going to pass them into your function as strings.
	There's one exception, and that's for flags.
- __We'll inspect your tasks as much as we can__ -- the `inspect` module is
	extremely powerful, and we'll glean as much as possible about the arg
	spec, documentation, name, etc. of your function as possible. You 
	shouldn't be burdened by telling _us_ what we can find out programatically
- __Tasks should be accessible__ -- whether it's the command-line, through
	the browser, or through a chat client, the tasks you define should be 
	easily accessed

Installing Shovel
-----------------

Like most python projects, build with the included `setup.py`:

	python setup.py install

Currently there are two dependencies:

	# You'll need argparse
	pip install argparse
	# If you want to run the web app, you'll need bottle, too
	pip install bottle

Using Shovel
------------

Shovel looks for a file in the current working directory called `shovel.py`
and executes it to find tasks you've defined (more on that in a second). If
you'd like to modularize your tasks, create a `shovel` directory, and put
as many python files as you'd like in that directory, and make as many files
as you'd like in there. Do this recursively if you'd like. For example:

	shovel/
		foo.py
		bar.py
		testing/
			foo.py
			zod.py
		util/
			hello.py

In this way, you can 'modularize' your tasks. By 'modularize,' these are not
full python modules (and we don't currently examing `__init__.py` in each 
directory), but it makes it convenient for organization. Each task is prepended
with the file and directory names. For example, if your `shovel/testing/foo.py`
defined a task `bar`, then that task would have the name `testing.foo.bar`.

If you define tasks in `shovel.py` instead of using a `shovel` directory, those
tasks will be in the global namespace. If `shovel.py` defines a task `bar`, then
that task's name would simply be `bar`.

In these python files, use shovel by importing shovel's task decorator. Then,
apply as needed:

	from shovel import task
	
	@task
	def hello(name):
		'''Prints hello and the provided name'''
		print 'Hello, %s' % name
	
	def not_a_task():
		'''Print I'm not considered a task in shovel'''
		pass

Global Tasks
------------
You can now also keep a `~/.shovel.py` file or `~/.shovel` directory and to
make tasks globally available.

Command Line Utility
--------------------
Invoke shovel with the `shovel` command. If you would like to know more about
what functions that shovel knows about, ask `shovel help` or `shovel tasks`.

If you'd like more information on a specific task or module, you can ask for
more information with shovel help. Shovel can figure out lots of things about
your tasks. Their names, file, line number, arguments, default arguments, if
they take a variable number of parameters, and so forth. When you ask for help
on a specific task, everything we know about that task will be presented to you.

	# List the tasks in the testing directory
	shovel help testing
	# Get more help on the testing.test task
	shovel help testing.test

Execute tasks with shovel and then the task name

	shovel foo.hello

Arguments are passed in a strings, and we really try to give you the same
semantics as when you'd normally invoke a function in python. For example,
arguments are considered positional arguments by default, but you can provide
a keyword name for specificity. For example, to execute `foo.bar` in a way
equivalent to `foo('1', '2', '3', hello='7')`, you would invoke it:

	shovel foo.bar 1 2 3 --hello 7

Keyword names are merely stripped of the leading dashes when parsed. Also
be warned that shovel options (like `--verbose` and `--dry-run`) will __not__
be available to your function. Speaking of which, if you would like shovel
to be extra talkative (for debugging, perhaps), use the `--verbose` switch:

	shovel --verbose foo.bar 1 2 3 --hello 7

Shovel has a dry-run option that will accept all the parameters you would 
normally pass into a task, but merely tells you how it would invoke a task.
This can be helpful if you want to inspect the arguments that your task 
would get, to make sure that it's correctly invoked:

	shovel --dry-run foo.bar 1 2 3 --hello 7

The one exception to arguments not being interpreted as strings is that 
orphan keyword arguments are interpreted as flags meaning 'True.' For example,
if we executed the following, then `a` and `b` would be passed as True:

	shovel foo.bar --a --b

The reason for this is that flags are common for tasks, and it's a relatively
unambiguous syntax. To a human, the meaning is clear, and now it is to shovel.

Server and Campfire
===================
The `shovel` utility used to ship with a server for making shovel tasks availble
through the browser, as well as campfire bot. These have now been moved into
their own repos for clarity and modularity:
[shovel-server](https://github.com/dlecocq/shovel-server) and
[shovel-campfire](https://github.com/seomoz/shovel-campfire). It's unclear how
much updating will need to be done to those projects, but they can now be
developed independently.

Command Line Auto-Complete
==========================
Because typing is no fun, the `completions/` directory has information on how
to set up auto-completion with different shells (currently only `zsh`). Thanks
to `philadams` for starting this set of helpers!

Motivation
==========

We had a project that had a fair number of semi-regularly used operational 
tasks, and we got sick of copy-and-paste, and we also didn't want to have
a standalone script complete with argparse for each and every one. We didn't
like the alternatives out there, and so, `shovel`. The original version 
constituted a weekend of work, and we've been eating our dog food ever since.

Recently, we realized that a lot of these operational details were intuitive
enough that we thought some of our support staff would want to make use of
them. Rather than make them keep a copy of the code checked out locally, and
use the command line, we figured it would be easiest to make HTTP endpoints
for them. That way, we could just add buttons to existing interfaces, and life
would be good.

We soon realized that while a nice interface, it's a pain to maintain endpoints
and command line tasks. So, why not make an interface that just runs those
same tasks and does a little bit of presentation to make it a web interface?
So now, without any additional work, you can start up the `shovel-server` and
have access to all of the tasks you've been using from the command line. In
this way, as developers we can keep one machine up to date and ready to run
code, and still provide access to staff outside of the project.

Contributing
============
Pull requests and bug reports are welcome. For bugs, please check that the
issue exists on the `master` branch before submitting a bug. Also, please
include an example along with the current behavior and the expected behavior.
Bonus points for adding a failing test.

For pull requests, you'll need to add or change tests in support of your
proposed change. To run the tests:

```python
python setup.py nosetests
```

This installs all the packages required to run tests, runs the tests and
provides coverage information.
