import sqlite3
from db_tools import constant
from entities import User, AccessRight
import logging

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

class AccessRightProperties:
	@constant
	def ID():
		return "id"

	@constant
	def DISPLAY():
		return "display"
	
USER_PROPS = UserProperties()
ACCRIGHT_PROPS = AccessRightProperties()

class UserContext:
	def __init__(self, db_path):
		logging.info("creating UserContext")
		self.db_path = db_path
		self.connection = None

	def __del__(self):
		logging.info("dropping UserContext")
		if self.connection != None:
			logging.info(f"closing connection to '{self.db_path}'.")
			self.connection.close()

	# Not tested yet
	def add_user(self, name) -> User:
		statement = "INSERT INTO Users (Name) VALUES('?');"

		with self.__get_connection__() as con:
			cur = con.execute(statement, (name,))

			if cur.rowcount != 1:
				raise ValueError(f"Expected one row to be added but was {cur.rowcount}")

		return self.get_user_by_name(self, name)

	def get_access_rights(self):
		con = self.__get_connection__()
		cur = con.cursor()

		statement = "SELECT Id, Display FROM AccessRights"

		for row in cur.execute(statement):
			yield AccessRight(row[ACCRIGHT_PROPS.ID], row[ACCRIGHT_PROPS.DISPLAY])


	def update_master(self):
		master = self.get_user_by_name("Master")

		if master == None:
			master = self.add_user("Master")

		for right in self.get_access_rights():
			if not master.has_right(right.display):
				self.add_user_right(master.id, right.id)


	def add_user_right(self, user_id, right_id):
		statement = "INSERT INTO UserRights (UserId, RightId) VALUES (?, ?)"

		with self.__get_connection__() as con:
			cur = con.execute(statement, (user_id, right_id,))

			if cur.rowcount != 1:
				raise ValueError(f"Expected one row to change but was {cur.rowcount}")

	def get_user_by_id(self, id) -> User:
		return self.get_single_user_where(f"{USER_PROPS.USER_ID} == {id}")

	def get_user_by_name(self, name) -> User:
		return self.get_single_user_where(f"{USER_PROPS.USER_NAME} == '{name}'")

	def get_single_user_where(self, predicate) -> User:
		user_list = self.get_users_where(predicate)

		user = next(user_list)

		if next(user_list, None) != None:
			raise ValueError(f"get_users_where('{predicate}') returned multiple results.")

		return user
			
	def get_users_where(self, predicate):
		con = self.__get_connection__()
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
			yield user

	def change_password(self, user, pwd):
		if user == None:
			raise ValueError("User must be specified.")

		if pwd == None or pwd == "":
			raise ValueError("User password cannot be null or empty.")

		pwd_hash = user.encrypt_pwd(pwd)

		if pwd_hash == None or pwd_hash == "":
			raise ValueError("Failed to encrypt password.")

		statement = "UPDATE Users SET PasswordHash = ? WHERE Id = ?;"

		with self.__get_connection__() as con:
			cur = con.execute(statement, (pwd_hash, user.id,))

			if cur.rowcount != 1:
				raise ValueError(f"Expected one row to change but was {cur.rowcount}")

			# for tests, check if password change is propagated to db
			statement = "SELECT PasswordHash FROM Users WHERE Id = ? AND PasswordHash = ?;"
			cur = con.execute(statement, (user.id, pwd_hash,))
			check_hash_row = cur.fetchone()
			if check_hash_row["PasswordHash"] != pwd_hash:
				raise ValueError("Failed to update password hash.")
			#con.commit()

	def __get_connection__(self):
		if self.connection == None:
			logging.info(f"creating new database connection to '{self.db_path}'.")
			self.connection = sqlite3.connect(self.db_path)
			self.connection.row_factory = sqlite3.Row
		else:
			logging.info(f"UserContext: reusing connection")

		return self.connection