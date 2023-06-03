
import sqlite3
from entities import Tarp, TarpCategory, TarpType, Damage
from db_tools import constant
import logging

class TarpsProperties:
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

TARPS_PROPS = TarpsProperties()

class TarpsContext:
	def __init__(self, db_path):
		logging.info("creating TarpsContext")
		self.db_path = db_path
		self.connection = None

	def __del__(self):
		logging.info("dropping TarpsContext")
		if self.connection != None:
			logging.info(f"closing connection to '{self.db_path}'.")
			self.connection.close()

	def select_by_numbers(self, number_list, order_by):
		predicate = self.make_predicate(TARPS_PROPS.TARP_NUMBER, number_list)
		return self.select(predicate, order_by)

	def select_by_category(self, category_list, order_by):
		predicate = self.make_predicate(TARPS_PROPS.CAT_NAME, category_list)
		return self.select(predicate, order_by)

	def select_by_type(self, tarp_types, order_by):
		predicate = self.make_predicate(TARPS_PROPS.TYPE_NAME, tarp_types, True)
		return self.select(predicate, order_by)

	def select_by_damage(self, damage_list, order_by):
		predicate = self.make_predicate(TARPS_PROPS.DMG_CODE, damage_list)
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

	def select(self, selection = None, order_by = None):
		con = self.__get_connection__()
		cur = con.cursor()
		tarp_list = []
		last_id = -1
		tarp = None
		damages = []

		statement = f"SELECT t.Id AS {TARPS_PROPS.TARP_ID}, t.Number AS {TARPS_PROPS.TARP_NUMBER}, t.Annotation AS {TARPS_PROPS.TARP_ANNO}, " \
		f"c.Id as {TARPS_PROPS.CAT_ID}, c.Name as {TARPS_PROPS.CAT_NAME}, c.Width as {TARPS_PROPS.CAT_WIDTH}, c.Length as {TARPS_PROPS.CAT_LENGTH}, c.Additional as {TARPS_PROPS.CAT_ADD}, " \
		f"y.Id as {TARPS_PROPS.TYPE_ID}, y.Name as {TARPS_PROPS.TYPE_NAME}, " \
		f"d.Id as {TARPS_PROPS.DMG_ID}, d.Code as {TARPS_PROPS.DMG_CODE}, d.Description as {TARPS_PROPS.DMG_DESC} " \
		"FROM Tarps AS t " \
		"JOIN Categories AS c ON t.CategoryId = c.Id " \
		"JOIN TarpTypes AS y ON c.TarpTypeId = y.Id " \
		"LEFT JOIN TarpDamages AS td ON t.Id = td.TarpId " \
		"LEFT JOIN Damages AS d ON td.DamageId = d.Id "

		if selection != None:
			statement += selection.to_sql()
			selected_numbers = selection.selected_numbers
		else:
			selected_numbers = []

		for row in cur.execute(statement):

			tarp_id = row[TARPS_PROPS.TARP_ID]
			if tarp_id != last_id:
				last_id = tarp_id
				if tarp != None:
					tarp.damages = damages
					tarp.is_selected = tarp.number in selected_numbers
					tarp_list.append(tarp)
					damages = []

				tarp_type = TarpType(row[TARPS_PROPS.TYPE_ID], row[TARPS_PROPS.TYPE_NAME])
				category = TarpCategory(row[TARPS_PROPS.CAT_ID], row[TARPS_PROPS.CAT_NAME], row[TARPS_PROPS.CAT_WIDTH],  row[TARPS_PROPS.CAT_LENGTH], row[TARPS_PROPS.CAT_ADD], tarp_type)
				tarp = Tarp(row[TARPS_PROPS.TARP_ID], row[TARPS_PROPS.TARP_NUMBER], row[TARPS_PROPS.TARP_ANNO], category, damages)

			if row[TARPS_PROPS.DMG_ID] != None:
				damage = Damage(row[TARPS_PROPS.DMG_ID], row[TARPS_PROPS.DMG_CODE], row[TARPS_PROPS.DMG_DESC])			
				damages.append(damage)

		if tarp != None:
			tarp.damages = damages
			tarp.is_selected = tarp.number in selected_numbers
			tarp_list.append(tarp)

		return tarp_list


	def is_pattern_property(self, property):
		if property == "None":
			return False
		elif property == TARPS_PROPS.CAT_ID:
			return False
		elif property == TARPS_PROPS.CAT_NAME:
			return False
		elif property == TARPS_PROPS.CAT_LENGTH:
			return False
		elif property == TARPS_PROPS.CAT_WIDTH:
			return False
		elif property == TARPS_PROPS.CAT_ADD:
			return False
		elif property == TARPS_PROPS.DMG_ID:
			return False
		elif property == TARPS_PROPS.DMG_CODE:
			return False
		elif property == TARPS_PROPS.DMG_DESC:
			return True
		elif property == TARPS_PROPS.TARP_ID:
			return False
		elif property == TARPS_PROPS.TARP_NUMBER:
			return False
		elif property == TARPS_PROPS.TARP_ANNO:
			return True
		elif property == TARPS_PROPS.TYPE_ID:
			return False
		elif property == TARPS_PROPS.TYPE_NAME:
			return True
		else:
			raise Exception(f"Unknown property '{property}'.")
		
	def __get_connection__(self):
		if self.connection == None:
			logging.info(f"creating new database connection to '{self.db_path}'.")
			self.connection = sqlite3.connect(self.db_path)
			self.connection.row_factory = sqlite3.Row
		else:
			logging.info(f"TarpsContext: reusing connection")

		return self.connection