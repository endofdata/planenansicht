from user_context import UserContext
from tarps_context import TarpsContext
from environment import env;
from flask import render_template
from contextvars import ContextVar
from routing import ROUTING

_request_context = ContextVar("request_context")

class RequestContext:
	def __init__(self):
		self._db_user = None
		self._db_tarps = None
		self._auth_context = None

	def __del__(self):
		if self._db_user != None:
			del self._db_user
			self._db_user = None
		if self._db_tarps != None:
			del self._db_tarps
			self._db_tarps = None

	def __getattr__(self, name):		
		if name == "user_context":
			if self._db_user == None:
				self._db_user = UserContext(env.db_users)
			return self._db_user
		elif name == "tarps_context":
			if self._db_tarps == None:
				self._db_tarps = TarpsContext(env.db_tarps)
			return self._db_tarps
		elif name == "auth_context":
			return self._auth_context
		else:
			raise AttributeError(f"Attribute '{name}' is not defined.")

	def __setattr__(self, name, value):
		if name == "auth_context":
			object.__setattr__(self, "_auth_context", value)
		elif name == "_db_user":
			object.__setattr__(self, name, value)
		elif name == "_db_tarps":
			object.__setattr__(self, name, value)
		elif name == "_auth_context":
			object.__setattr__(self, name, value)
		else:
			raise AttributeError(f"Attribute '{name}' cannot be set.")

	def view_result(self, name, **kwargs):
		return render_template(name, ROUTING=ROUTING, auth_context=self.auth_context, **kwargs)