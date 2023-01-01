from flask import Blueprint, request, redirect, url_for
from werkzeug.local import LocalProxy
from routing import *
from request_context import _request_context
from authorization import authorize
import logging

request_context = LocalProxy(_request_context)

admin_api = Blueprint(ADMIN_API_NAME, __name__)

@admin_api.route(UPDATE_MASTER_ENDPOINT, methods = ['GET'])
@authorize("user", access="UpdateMaster")	
def update_master():
	logging.info("updating master account")
	user_context = request_context.user_context
	user_context.update_master()
	return redirect(url_for(AUTH_LOGIN))

@admin_api.route(LIST_USERS_ENDPOINT, methods = ['GET'])
@authorize("user", access="ListUsers")	
def list_users():
	user_context = request_context.user_context
	user_list = user_context.get_users_where("TRUE")
	return request_context.view_result("users_list.html.jinja", user_list = user_list)		


@admin_api.route(ADD_USER_ENDPOINT, methods = ['GET', 'POST'])
@authorize("user", access="AddUser")	
def add_user():
	if request.method == 'GET':
		return request_context.view_result("add_user.html.jinja")		
	else:
		logging.info("add user account")

