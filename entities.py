class Damage:
	def __init__(self, id, code, description):
		self.id = id
		self.code = code
		self.description = description

class TarpType:
	def __init__(self, id, name):
		self.id = id
		self.name = name

class TarpCategory:
	def __init__(self, id, name, width, length, additional, tarp_type):
		self.id = id
		self.name = name
		self.width = width
		self.length = length
		self.additional = additional
		self.tarp_type = tarp_type

class Tarp:
	def __init__(self, id, number, annotation, category, damages):
		self.id = id
		self.number = number
		self.annotation = annotation
		self.category = category
		self.damages = damages

