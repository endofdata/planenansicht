from flask import Blueprint, request, redirect, url_for
from werkzeug.local import LocalProxy
from routing import *
from user_context import USER_PROPS, ACCRIGHT_PROPS
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
@authorize("user", access="ViewUsers")	
def list_users():
	user_context = request_context.user_context
	user_list = user_context.get_users_where("TRUE")
	return request_context.view_result("user_list.html.jinja", USER_PROPS=USER_PROPS, user_list = user_list)

@admin_api.route(ADD_USER_ENDPOINT, methods = ['GET'])
@authorize("user", access="AddUsers")	
def add_user():
	logging.info("add user account")
	user_context = request_context.user_context
	name = request.args[USER_PROPS.USER_NAME]
	display = request.args[USER_PROPS.USER_DSP]
	user_context.add_user(name, display)
	return redirect(url_for(ADMIN_LIST_USERS))

@admin_api.route(DELETE_USER_ENDPOINT, methods = ['GET'])
@authorize("user", access="DeleteUsers")	
def delete_user():
	logging.info("delete user account")
	user_context = request_context.user_context
	id = request.args[USER_PROPS.USER_ID]
	user_context.delete_user(id)
	return redirect(url_for(ADMIN_LIST_USERS))

@admin_api.route(EDIT_USER_ENDPOINT, methods = ['GET', 'POST'])
@authorize("user", access="EditUsers")	
def edit_user():
	logging.info("edit user account")
	user_context = request_context.user_context

	if request.method == 'POST':
		id = request.form[USER_PROPS.USER_ID]
		name = request.form[USER_PROPS.USER_NAME]
		display = request.form[USER_PROPS.USER_DSP]
		user_context.update_user(id, name, display)
	else:
		id = request.args[USER_PROPS.USER_ID]

	user = user_context.get_user_by_id(id)

	return request_context.view_result("user_details.html.jinja", USER_PROPS=USER_PROPS, user = user)

@admin_api.route(EDIT_USERRIGHTS_ENDPOINT, methods = ['POST'])
@authorize("user", access="EditUserRights")	
def edit_user_rights():
	logging.info("edit user rights")
	user_context = request_context.user_context

	id = request.form[USER_PROPS.USER_ID]
	user = user_context.get_user_by_id(id)

	# get list of existing rights
	all_rights = list(user_context.get_access_rights())

	old_rights = filter(lambda r: request.form.get(r.display) == None, user.rights)

	for right in old_rights:
		user_context.delete_user_right(user.id, right.id)

	new_rights = filter(lambda r: request.form.get(r.display) != None, all_rights)

	for right in new_rights:
		user_context.add_user_right(user.id, right.id)

	return request_context.view_result("user_details.html.jinja", USER_PROPS=USER_PROPS, user = user)