from bcrypt import hashpw, gensalt, checkpw
from base64  import b64encode
from hashlib import sha256

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

class Selector:
	def __init__(self, property = None, values = None, is_pattern = False):
		self.property = property
		self.values = values
		self.is_pattern = is_pattern

	def to_sql(self):
		predicate = ""

		if self.property != None:
			if len(self.values) > 0:
				for value in self.values:
					if self.is_pattern:
						predicate += f"({self.property} LIKE '%{value}%') OR "
					else:
						predicate += f"({self.property} = '{value}') OR "

				# strip trailing "OR "
				predicate = predicate[0:-3]
			else:
				predicate = f"{self.property} IS NULL"

		return predicate

class Order:
	def __init__(self, property = None, is_descending = False):
		self.property = property
		self.is_descending = is_descending

	def to_sql(self):
		sql = ""

		if self.property != None:
			if self.is_descending:
				dir = "DESC"
			else:
				dir = "ASC"

			sql = f"{self.property} {dir}"
		
		return sql

class Selection:
	def __init__(self, selectors, sequence):
		self.selectors = selectors
		self.sequence = sequence

	def has_selectors(self):
		for selector in self.selectors:
			if selector.property != None:
				return True

		return False

	def has_sequence(self):
		for order in self.sequence:
			if order.property != None:
				return True

		return False

	def to_sql(self):
		predicate = ""

		if self.has_selectors():
			predicate += " WHERE "

			for selector in self.selectors:
				if selector.property != None:
					predicate += f"({selector.to_sql()}) AND "
			
			# strip trailing 'AND '
			predicate = predicate[0:-4]

		if self.has_sequence():
			predicate += " ORDER BY "
			for order in self.sequence:
				if order.property != None:
					predicate += f"{order.to_sql()}, "

			#strip trailin ', '
			predicate = predicate[0:-2]

		return predicate

class User:
	def __init__(self, id, name, display, pwd_hash, rights):
		self.id = id
		self.name = name
		self.display = display
		self.pwd_hash = pwd_hash
		self.rights = rights

	def encrypt_pwd(self, pwd):    
		self.pwd_hash = hashpw(b64encode(sha256(pwd.encode()).digest()), gensalt()).decode()
		
	def check_pwd(self, pwd):
		return checkpw(b64encode(sha256(pwd.encode()).digest()), self.pwd_hash.encode())

class AccessRight:
	def __init__(self, id, display):
		self.id = id
		self.display = display
