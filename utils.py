from html.parser import HTMLParser

def load_csv(filename : str):
	with open(filename, 'r', newline='') as file:
		content = file.read()
		if content == '':
			return []
		else:
			return [value for value in content.split(';') if value != '']

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