from bcrypt import hashpw, gensalt, checkpw
from base64  import b64encode
from hashlib import sha256

class Damage:
	"""Defines a certain kind of a damage, like 'Knopf fehlt' or 'Riss'
	
	This is the entity type for data rows in the Damages table of the Tarps database.
	If multiple tarps have comparable issues, they can share the same Damage definition
	"""
	def __init__(self, id, code, description):
		self.id = id
		self.code = code
		self.description = description

class TarpType:
	"""Defines a tarp type i.e., 'Kotenplane' or 'Jurtenopi'
	
	This is the entity type for data rows in the TarpTypes table of the Tarps database.
	"""
	def __init__(self, id, name):
		self.id = id
		self.name = name

class TarpCategory:
	"""Defines a tarp category e.g., the 'A', 'B' or 'C' category of tarp type 'Kotenplane'

	This is the entity type for data rows in the Categories table of the Tarps database.
	"""
	def __init__(self, id, name, width, length, additional, tarp_type):
		self.id = id
		self.name = name
		self.width = width
		self.length = length
		self.additional = additional
		self.tarp_type = tarp_type

class Tarp:
	"""Defines a tarp including annotation, category and damages

	This is the entity type for data rows in the Tarps table of the Tarps database.
	"""
	def __init__(self, id, number, annotation, category, damages):
		self.id = id
		self.number = number
		self.annotation = annotation
		self.category = category
		self.damages = damages


class User:
	"""Defines a user who is allowed to work on the Tarps database

	This is the entity type for data rows in the Users table of the Users database.
	"""
	def __init__(self, id, name, display, pwd_hash, rights):
		self.id = id
		self.name = name
		self.display = display
		self.pwd_hash = pwd_hash
		self.rights = rights

	def encrypt_pwd(self, pwd):
		"""Updates the pwd_hash based on the specified pwd

		Generates a hashed password using the base-64 encoded SHA-256 of the specified pwd and stores
		it in self.pwd_hash.

		Args:
			pwd: new password as entered by the user

		Returns:
			The new value of pwd_hash
		"""
		if pwd == None or pwd == "":
			raise ValueError("The password cannot be empty or unset")
		self.pwd_hash = hashpw(b64encode(sha256(pwd.encode()).digest()), gensalt()).decode()
		return self.pwd_hash
		
	def check_pwd(self, pwd):
		"""Validates the specified pwd based on the previously stored pwd_hash

			Checks a hashed password generated from the base-64 encoded SHA-256 of the specified pwd
			against the previously stored pwd_hash.

		Args:
			pwd: password as entered by the user

		Returns:
			True if the validation was successful e.g., the pwd is correct. Otherwise false.
		"""
		if pwd == None or pwd == "":
			return False
		return checkpw(b64encode(sha256(pwd.encode()).digest()), self.pwd_hash.encode())

class AccessRight:
	"""Defines a permission for a certain program function

	This is the entity type for data rows in the AccessRights table of the Users database.
	"""
	def __init__(self, id, display):
		self.id = id
		self.display = display
