from werkzeug.local import LocalProxy
from flask import abort
from request_context import _request_context
from db_tools import constant
from functools import wraps

request_context = LocalProxy(_request_context)

class AuthorizationResult:
	@constant
	def FORBIDDEN():
		return -1

	@constant
	def NONE():
		return 0

	@constant
	def ALLOW():
		return 1

class AuthorizationPolicy:
	def __init__(self, name, handlers):
		self.name = name
		self.handlers = handlers

	def execute(self):
		for handler in self.handlers:
			authz_result = handler(request_context)
			if authz_result == AuthorizationResult.FORBIDDEN:
				return authz_result
			elif authz_result == AuthorizationResult.ALLOW:
				return authz_result
		return AuthorizationResult.NONE			

__policies__ = dict()

def register_policy(policy):
	__policies__[policy.name] = policy

def authorize(policy):
	def authorize_decorator(func):
		@wraps(func)
		def func_wrapper():
			if policy in __policies__:
				authz_result = __policies__[policy].execute()
				if authz_result == AuthorizationResult.FORBIDDEN:
					abort(403)
				else:
					return func()
			else:
				abort(403)
		return func_wrapper
	return authorize_decorator

