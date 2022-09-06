from flask import Blueprint, render_template, request, session, redirect, url_for
from user_context import USER_PROPS, UserContext
from environment import env
from werkzeug.local import LocalProxy
from request_context import _request_context
from routing import *
import logging

authentication_api = Blueprint(AUTH_API_NAME, __name__)
request_context = LocalProxy(_request_context)

class AuthenticationContext:
	def __init__(self):
		self.user = None

def authenticate():
	logging.info(f"authentication for: '{request.method} {request.url}'")
	auth_context = request_context.auth_context
	if auth_context == None:
		auth_context = AuthenticationContext()
		request_context.auth_context = auth_context

	if request.path == LOGIN_ENDPOINT:
		logging.info("login in progress")			
		auth_context.user = None 
	elif USER_PROPS.USER_NAME in session:
		user_context = request_context.user_context
		auth_context.user = user_context.get_user_by_name(session[USER_PROPS.USER_NAME])
		if auth_context.user == None or auth_context.user.pwd_hash == None:
			logging.info(f"authenticating user '{auth_context.user.name}'.")
			if auth_context.user.pwd_hash == None and not request.path.startswith(USER_API_AREA):
				logging.info(f"user '{auth_context.user.name}' must change password.")
				return redirect(url_for(USER_CHANGE_PASSWORD))
			else:
				logging.info(f"user '{auth_context.user.name}' is authenticated.")
		else:
			logging.info(f"authenticated user is '{auth_context.user.name}'.")
	else:
		auth_context.user = None
		logging.info("Login required")
		return redirect(url_for(AUTH_LOGIN))		

@authentication_api.route(LOGIN_ENDPOINT, methods = ['GET', 'POST'])
def login():
	if request.method == "GET" or request.form[USER_PROPS.USER_NAME] == None:
		return render_template("login.html.jinja", USER_PROPS=USER_PROPS, ROUTING=ROUTING)
	else:
		user_name = request.form[USER_PROPS.USER_NAME]
		redir = None
		user_context = request_context.user_context
		user = user_context.get_user_by_name(user_name)		
		if user == None:
			redir = AUTH_LOGIN
			logging.info(f"user '{user_name}' was not found.")
		else:			
			if user.pwd_hash == None:
				session[USER_PROPS.USER_NAME] = user.name
				redir = USER_CHANGE_PASSWORD
				logging.info(f"user '{user.name}' has no password yet.")
			elif user.check_pwd(request.form[USER_PROPS.USER_PASSWORD]):
				session[USER_PROPS.USER_NAME] = user.name
				redir = ROOT_ACTION
				logging.info(f"user '{user.name}' password check successful.")
			else:
				redir = AUTH_LOGIN
				logging.info(f"user '{user.name}' password check failed.")

		logging.info(f"redirecting to '{redir}'.")
		return redirect(url_for(redir))

@authentication_api.route(LOGOUT_ENDPOINT, methods = ['GET'])
def logout():
	session.clear()
