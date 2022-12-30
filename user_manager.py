from flask import Blueprint, request, redirect, url_for
from environment import env
from db_tools import constant
from routing import *
from werkzeug.local import LocalProxy
from request_context import _request_context
from authorization import authorize
import logging

request_context = LocalProxy(_request_context)

user_api = Blueprint(USER_API_NAME, __name__)

class UserApiProperties:
	@constant
	def NEW_PASSWORD():
		return "new_password"

	@constant
	def REP_PASSWORD():
		return "rep_password"

USERAPI_PROPS = UserApiProperties()

@user_api.route(CHANGE_PASSWORD_ENDPOINT, methods = ['GET', 'POST'])
@authorize("user", access="ChangePassword")
def change_password():
	authed_user = request_context.auth_context.user

	if authed_user == None:
		raise ValueError("WTF are we doing here=")

	if request.method == 'GET':
		return request_context.view_result("change_pwd.html.jinja", USERAPI_PROPS=USERAPI_PROPS)		
	else:
		new_pwd = request.form[USERAPI_PROPS.NEW_PASSWORD]
		if new_pwd != request.form[USERAPI_PROPS.REP_PASSWORD]:
			return request_context.view_result("change_pwd.html.jinja", USERAPI_PROPS=USERAPI_PROPS)		

		user_context = request_context.user_context
		user_context.change_password(authed_user, new_pwd)

		logging.info(f"changed password for user '{authed_user.name}'")
		logging.info(f"redirecting to '{AUTH_LOGIN}'.")
		return redirect(url_for(AUTH_LOGIN))


@user_api.route(UPDATE_MASTER_ENDPOINT, methods = ['GET'])
def update_master():
	logging.info("updating master account")
	user_context = request_context.user_context
	user_context.update_master()
	return redirect(url_for(AUTH_LOGIN))

