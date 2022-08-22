
import sqlite3
from entities import Tarp, TarpCategory, TarpType, Damage

class DbContext:
	def __init__(self, db_path):
		self.db_path = db_path

	def select_by_numbers(self, number_list):
		predicate = ""
		for num in number_list:
			predicate += f" (number = {num}) OR"
		if predicate.endswith(" OR"):
			predicate = predicate[0:-3]

		return self.select(predicate, 'number')

	def select_by_category(self, category):
		predicate = f"cat_name LIKE '%{category}%'"

		return self.select(predicate, 'number')

	def select_by_type(self, tarp_type):
		predicate = f"type_name LIKE '%{tarp_type}%'"

		return self.select(predicate, 'number')

	def select_by_damage(self, damage_list):
		predicate = ""
		for code in damage_list:
			predicate += f" (dmg_code = '{code}') OR"
		if predicate.endswith(" OR"):
			predicate = predicate[0:-3]

		return self.select(predicate, 'number')

	def select(self, predicate = None, order_by = None):
		con = sqlite3.connect(self.db_path)
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		tarp_list = []
		last_id = -1
		tarp = None
		damages = []

		statement = "SELECT t.Id AS id, t.Number AS number, t.Annotation AS annotation, " \
		"c.Id as cat_id, c.Name as cat_name, c.Width as cat_w, c.Length as cat_l, c.Additional as cat_a, " \
		"y.Id as type_id, y.Name as type_name, " \
		"d.Id as dmg_id, d.Code as dmg_code, d.Description as dmg_desc " \
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

			tarp_id = row["id"]
			if tarp_id != last_id:
				last_id = tarp_id
				if tarp != None:
					tarp.damages = damages
					tarp_list.append(tarp)
					damages = []

				tarp_type = TarpType(row["type_id"], row["type_name"])
				category = TarpCategory(row["cat_id"], row["cat_name"], row["cat_w"],  row["cat_l"], row["cat_a"], tarp_type)
				tarp = Tarp(row["id"], row["number"], row["annotation"], category, damages)

			damage = Damage(row["dmg_id"], row["dmg_code"], row["dmg_desc"])
			damages.append(damage)

		if tarp != None:
			tarp.damages = damages
			tarp_list.append(tarp)

		return tarp_list