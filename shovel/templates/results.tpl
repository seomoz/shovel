<html>
	<head>
		<title>{{ task.fullname }}</title>
		<link rel='stylesheet' href='static/css/style.css' type='text/css' />
	</head>
	<body>
		<div class='task-container'>
			<div class='task-name'>
				{{ task.fullname }}{{ args }}
			</div>
			
			%import cgi
			%if results['stdout'] != None:
			<div class='task-result'>
				stdout: <div class='task-stdout'>{{! cgi.escape(results['stdout']).replace('\n', '<br/>') }}</div>
			</div>
			%end
			
			%if results['stderr'] != None:
			<div class='task-result'>
				stderr: <div class='task-stderr'>{{! cgi.escape(results['stderr']).replace('\n', '<br/>')}}</div>
			</div>
			%end
			
			%if results['return'] != None:
			<div class='task-result'>
				returned: <div class='task-returned'>{{! cgi.escape(results['return']).replace('\n', '<br/>')}}</div>
			</div>
			%end
			
			%if results['exception'] != None:
			<div class='task-result'>
				exception: <div class='task-exception'>{{! cgi.escape(results['exception']).replace('\n', '<br/>')}}</div>
			</div>
			%end
		</div>
	</body>
</html>
