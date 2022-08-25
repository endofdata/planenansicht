
import sqlite3
from entities import Tarp, TarpCategory, TarpType, Damage

def constant(f):
	def fset(self, value):
		raise TypeError
	def fget(self):
		return f()
	return property(fget, fset)

class Properties:
	@constant
	def TARP_ID():
		return "id"

	@constant
	def TARP_NUMBER():
		return "number"

	@constant
	def TARP_ANNO():
		return "annotation"

	@constant
	def CAT_ID():
		return "cat_id"

	@constant
	def CAT_NAME():
		return "cat_name"

	@constant
	def CAT_WIDTH():
		return "cat_w"

	@constant
	def CAT_LENGTH():
		return "cat_l"

	@constant
	def CAT_ADD():
		return "cat_a"

	@constant
	def TYPE_ID():
		return "type_id"
	
	@constant
	def TYPE_NAME():
		return "type_name"

	@constant
	def DMG_ID():
		return "dmg_id"

	@constant
	def DMG_CODE():
		return "dmg_code"

	@constant
	def DMG_DESC():
		return "dmg_desc"

PROPS = Properties()

class DbContext:
	def __init__(self, db_path):
		self.db_path = db_path

	def select_by_numbers(self, number_list, order_by):
		predicate = self.make_predicate(PROPS.TARP_NUMBER, number_list, True)
		return self.select(predicate, order_by)

	def select_by_category(self, category_list, order_by):
		predicate = self.make_predicate(PROPS.CAT_NAME, category_list, True)
		return self.select(predicate, order_by)

	def select_by_type(self, tarp_types, order_by):
		predicate = self.make_predicate(PROPS.TYPE_NAME, tarp_types, True)
		return self.select(predicate, order_by)

	def select_by_damage(self, damage_list, order_by):
		predicate = self.make_predicate(PROPS.DMG_CODE, damage_list)
		return self.select(predicate, order_by)

	def make_predicate(self, key, value_list, is_pattern = False):
		predicate = ""
		for code in value_list:
			if is_pattern:
				predicate += f" ({key} LIKE '%{code}%') OR"
			else:
				predicate += f" ({key} = '{code}') OR"

		if predicate.endswith(" OR"):
			predicate = predicate[0:-3]
		else:
			predicate = f" {key} IS NULL"

		return predicate

	def select(self, predicate = None, order_by = None):
		con = sqlite3.connect(self.db_path)
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		tarp_list = []
		last_id = -1
		tarp = None
		damages = []

		statement = f"SELECT t.Id AS {PROPS.TARP_ID}, t.Number AS {PROPS.TARP_NUMBER}, t.Annotation AS {PROPS.TARP_ANNO}, " \
		f"c.Id as {PROPS.CAT_ID}, c.Name as {PROPS.CAT_NAME}, c.Width as {PROPS.CAT_WIDTH}, c.Length as {PROPS.CAT_LENGTH}, c.Additional as {PROPS.CAT_ADD}, " \
		f"y.Id as {PROPS.TYPE_ID}, y.Name as {PROPS.TYPE_NAME}, " \
		f"d.Id as {PROPS.DMG_ID}, d.Code as {PROPS.DMG_CODE}, d.Description as {PROPS.DMG_DESC} " \
		"FROM Tarps AS t " \
		"JOIN Categories AS c ON t.CategoryId = c.Id " \
		"JOIN TarpTypes AS y ON c.TarpTypeId = y.Id " \
		"LEFT JOIN TarpDamages AS td ON t.Id = td.TarpId " \
		"LEFT JOIN Damages AS d ON td.DamageId = d.Id "

		if(predicate != None):
			statement += f" WHERE {predicate}"

		if order_by != None:
			statement += f" ORDER BY {order_by}"

		for row in cur.execute(statement):

			tarp_id = row[PROPS.TARP_ID]
			if tarp_id != last_id:
				last_id = tarp_id
				if tarp != None:
					tarp.damages = damages
					tarp_list.append(tarp)
					damages = []

				tarp_type = TarpType(row[PROPS.TYPE_ID], row[PROPS.TYPE_NAME])
				category = TarpCategory(row[PROPS.CAT_ID], row[PROPS.CAT_NAME], row[PROPS.CAT_WIDTH],  row[PROPS.CAT_LENGTH], row[PROPS.CAT_ADD], tarp_type)
				tarp = Tarp(row[PROPS.TARP_ID], row[PROPS.TARP_NUMBER], row[PROPS.TARP_ANNO], category, damages)

			if row[PROPS.DMG_ID] != None:
				damage = Damage(row[PROPS.DMG_ID], row[PROPS.DMG_CODE], row[PROPS.DMG_DESC])			
				damages.append(damage)

		if tarp != None:
			tarp.damages = damages
			tarp_list.append(tarp)

		return tarp_list