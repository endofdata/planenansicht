import sqlite3
from db_tools import constant
from entities import User, AccessRight

class UserProperties:
	@constant
	def USER_ID():
		return "user_id"

	@constant
	def USER_NAME():
		return "user_name"

	@constant
	def USER_DSP():
		return "user_dsp"

	@constant
	def USER_PWDHASH():
		return "user_pwdhash"

	@constant
	def USER_PASSWORD():
		return "user_password"

	@constant
	def RIGHT_ID():
		return "right_id"

	@constant
	def RIGHT_DSP():
		return "right_dsp"

USER_PROPS = UserProperties()

class UserContext:
	def __init__(self, db_path):
		self.db_path = db_path

	def get_user_by_id(self, id) -> User:
		return self.get_single_user_where(f"{USER_PROPS.USER_ID} == {id}")

	def get_user_by_name(self, name) -> User:
		return self.get_single_user_where(f"{USER_PROPS.USER_NAME} == '{name}'")

	def get_single_user_where(self, predicate) -> User:
		user_list = self.get_users_where(predicate)
		user_count = len(user_list)

		if user_count == 1:
			return user_list[0]
		elif user_count == 0:
			return None
		else:
			raise ValueError(f"get_users_where('{predicate}') returned {user_count} results.")
			
	def get_users_where(self, predicate):
		con = sqlite3.connect(self.db_path)
		con.row_factory = sqlite3.Row
		cur = con.cursor()
		user_list = []
		user = None
		rights = []
		last_id = None

		statement = f"SELECT "

		statement += f"u.Id AS {USER_PROPS.USER_ID}, u.Name AS {USER_PROPS.USER_NAME}, " \
		f"u.Display AS {USER_PROPS.USER_DSP}, u.PasswordHash AS {USER_PROPS.USER_PWDHASH}, " \
		f"a.Id AS {USER_PROPS.RIGHT_ID}, a.Display AS {USER_PROPS.RIGHT_DSP} " \
		"FROM Users AS u " \
		"LEFT JOIN UserRights AS r ON r.UserId = u.Id " \
		"LEFT JOIN AccessRights AS a ON a.Id = r.RightId " \
		f"WHERE {predicate}"

		for row in cur.execute(statement):

			user_id = row[USER_PROPS.USER_ID]
			if user_id != last_id:
				last_id = user_id
				if user != None:
					user.rights = rights
					user_list.append(user)
					rights = []

				user = User(row[USER_PROPS.USER_ID], row[USER_PROPS.USER_NAME], row[USER_PROPS.USER_DSP], row[USER_PROPS.USER_PWDHASH], rights)

			if row[USER_PROPS.RIGHT_ID] != None:
				right = AccessRight(row[USER_PROPS.RIGHT_ID], row[USER_PROPS.RIGHT_DSP])
				rights.append(right)

		if user != None:
			user.rights = rights
			user_list.append(user)

		return user_list