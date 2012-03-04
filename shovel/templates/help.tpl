<html>
	<head>
		<title>Help</title>
		<link rel='stylesheet' href='static/css/style.css' type='text/css' />
	</head>
	<body>
		%import re
		%for task in tasks:
		<div class='task-container'>
			<div class='task-name'>{{ task['full'] }}{{ task['args'] }}</div>
			<div class='task-file'>In {{ task['file'] }}:{{ task['line'] }}</div>
			<div class='task-doc' >
				{{! re.sub(r'(\s|^)(http://\S+)(\s|$)', r'\1<a href="\2">\2</a>\3', task['doc']).replace('\n', '<br/>') }}
			</div>
		</div>
		%end
	</body>
</html>
