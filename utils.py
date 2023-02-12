from html.parser import HTMLParser

def load_csv(filename : str):
	with open(filename, 'r', newline='') as file:
		content = file.read()
		if content == '':
			return []
		else:
			return [value for value in content.split(';') if value != '']

def parse(line : str) -> list:
	default_args = line.split()
	default_args[0] = default_args[0][1:] # Delete '!'

	args = []

	in_string = False
	for i in range(len(default_args)):
		if not in_string:
			if default_args[i][0] == '"':
				default_args[i] = default_args[i][1:]
				if len(default_args[i]) > 1 and default_args[i][-1] == '"':
					default_args[i] = default_args[i][:-1]
				else:
					in_string = True
			args.append(default_args[i])
		else:
			if default_args[i][-1] == '"':
				default_args[i] = default_args[i][:-1]
				in_string = False 
			args[-1] = args[-1] + " " + default_args[i]

	return args

def to_int(nb : str):
	try:
		converted_nb = int(nb)
		return converted_nb
	except ValueError:
		return None

def find_all(a_str : str, sub : str):
	indexs = []

	start = a_str.find(sub, 0)
	while start != -1:
		indexs.append(start)
		start += len(sub)
		start = a_str.find(sub, start)

	return indexs

class HTMLFilter(HTMLParser):
	text = ""
	def handle_data(self, data):
		self.text += data