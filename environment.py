from os import getenv, getcwd
from os import path
import logging
import secrets

class Environment:
	def __init__(self):
		self.log_level = getenv("TARPS_LOG_LEVEL", "INFO").upper()		
		self.db_root = getenv("TARPS_DATA_ROOT", path.relpath(getcwd(), "data"))		
		self.db_tarps = path.join(self.db_root, "tarps.sqlite")
		self.db_users = path.join(self.db_root, "users.sqlite")
		self.max_selectors = int(getenv("TARPS_MAX_SELECTORS", 3))
		self.max_orders = int(getenv("TARPS_MAX_ORDERS", 2))

	def log(self):
		logging.info(f"Using db_root '{self.db_root}'")
		logging.info(f"Number of filter selectors: {self.max_selectors}")
		logging.info(f"Number of sorting criteria: {self.max_orders}")

	def get_secret_key(self):
		key = getenv("TARPS_SECRET_KEY", None)
		if key == None:
			key = secrets.token_hex()
		return key

	def init_logging(self):
		numeric_level = getattr(logging, self.log_level, None)
		if not isinstance(numeric_level, int):
			raise ValueError(f"Unsupported TARPS_LOG_LEVEL='{self.log_level}'")
		logging.basicConfig(level=numeric_level)