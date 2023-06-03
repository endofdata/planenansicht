#from multiprocessing.sharedctypes import Value

class Selector:
	"""Describes a property and its values in a Selection"""
	def __init__(self, property = None, values = None, is_pattern = False):
		self.property = property
		self.values = values
		self.is_pattern = is_pattern

	def to_sql(self):
		"""Creates a partial SQL statement that can be used in a WHERE clause
		
		The generated SQL is a logical 'OR' combination comparing the property with each
		of the specified values. The is_pattern flag controls, whether a string pattern
		comparison or a direct value comparison is generated. If no values are specified,
		the generated SQL checks the property to be NULL. If no property name is specified,
		the result is an empty string.

		Examples:

		If property is set to 'category' and values are 'A' and 'D', the resulting SQL is:

		(category = 'A') OR (category = 'D')

		If property is set to 'annotation', values are 'rostig' and 'an der Kante' and 
		is_pattern is set to True, the resulting SQL is:

		(annotation LIKE '%rostig%') OR (annotation LIKE '%an der Kante%')

		If property is set to 'number' and no values are specified, the resulting SQL is:

		number IS NULL
		"""
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
	"""Describes the sorting directory for an SQL result"""
	def __init__(self, property = None, is_descending = False):
		self.property = property
		self.is_descending = is_descending

	"""Creates a partial SQL statement that can be used in an ORDER BY clause.

	The resulting SQL is the property name followed b y the SQL code for the sort direction,
	which is DESC when is_descending is set to True or ASC otherwise. If no property name is
	specified, the result is an empty string.

	Example:

	If property is set to 'annotation' and is_descending is set to False, the resulting SQL is:

	annotation ASC
	"""
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
	"""Defines a database selection based on property selectors and sorting sequence

	The selection can be formatted as partial SQL statement by calling the to_sql() method.
	"""
	def __init__(self, selectors, sequence, selected_numbers = None):
		"""Constructor

		Args:
			selectors: a list of zero or more Selector objects that define the filter criteria.
			sequence: a list of zero or more Order objects that define the sorting order of the result.
		"""
		self.selectors = selectors
		self.sequence = sequence
		self.selected_numbers = selected_numbers

	def has_selectors(self):
		"""Checks if the selectors list contains valid entries

		Returns:
			True, if there is at least one selector with a specified property name. False otherwise.
		"""
		for selector in self.selectors:
			if selector.property != None:
				return True

		return False

	def has_sequence(self):
		"""Checks if the sequence list contains valid entries
		
		Returns:
			True, if there is at least one entry in the sorting sequence list with a specified property name. False otherwise.
		"""
		for order in self.sequence:
			if order.property != None:
				return True

		return False

	def get_selected_numbers(self):
		if self.selected_numbers == None:
			return ''
		return ", ".join([str(x) for x in self.selected_numbers])

	def to_sql(self):
		"""Creates a partial SQL statement with optional WHERE and ORDER BY clauses

		If the selection has selectors, these are combined with logical 'AND' to form a WHERE clause. 
		
		If the selection has sequence items, these are listed comma-separated to form an ORDER BY clause.

		If neither selectors nor sequence items are defined, the result is an empty string. Otherwise, it
		either starts with ' WHERE ' or ' ORDER BY ' and can be appended to a SELECT statement.
		"""
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
