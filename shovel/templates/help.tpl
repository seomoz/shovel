<html>
	<head>
		<title>Help</title>
		<link rel='stylesheet' href='static/css/style.css' type='text/css' />
	</head>
	<body>
		%for task in tasks:
		<div class='task-container'>
			<div class='task-name'>{{ task['full'] }}{{ task['args'] }}</div>
			<div class='task-file'>In {{ task['file'] }}:{{ task['line'] }}</div>
			<div class='task-doc' >{{ task['doc'] }}</div>
		</div>
		%end
	</body>
</html>
