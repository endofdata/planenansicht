from environment import env
from flask import Flask, request
from tarps_context import TARPS_PROPS
from selection import Selector
from selection import Order
from selection import Selection
from entities import User;
from user_manager import user_api
from admin_api import admin_api
from authentication import authentication_api, authenticate
from authorization import AuthorizationPolicy, AuthorizationResult, authorize, register_policy
from routing import *
from request_context import RequestContext, _request_context
from werkzeug.local import LocalProxy
import logging
import click
from click import Context
from flask.cli import run_command
from typing import Optional, Any
from sys import exc_info
from ssl import create_default_context, Purpose

# TODO: Move to separate source
def authorize_user(request_context, access):
	usr = request_context.auth_context.user

	if usr == None:
		return AuthorizationResult.FORBIDDEN

	if (access != None) and (usr.has_right(access)):
			return AuthorizationResult.ALLOW

	return AuthorizationResult.NONE

# Debug helper: if you want to create a new password
# usr = User(0, "Master", "The master of desaster", None, None)
# pwd = usr.encrypt_pwd("master")
# is_valid = usr.check_pwd("master")

env.init_logging()
env.log()

request_context = LocalProxy(_request_context)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = env.get_secret_key()
app.register_blueprint(authentication_api)
app.register_blueprint(user_api)
app.register_blueprint(admin_api)

register_policy(AuthorizationPolicy("user", [ authorize_user]))
register_policy(AuthorizationPolicy("guest", [lambda context: AuthorizationResult.ALLOW]))

#------------------------------------------------------------------------------------------------------------------------------
# Not called when running flask
#------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	pass
#------------------------------------------------------------------------------------------------------------------------------


# While the click documentation does not recommend to forward commands, it does not name
# an alternative to it. But when --cert and --key are just forwarded to the Werkzeug stack
# where creation of the SSL/TLS context asks for a PEM password in the terminal. So, forwarding
# to the run_command after creating the SSL/TLS is currently the only known option.
# Note that the run_command supports some more parameters
@app.cli.command("run_ssl", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", default=5000, help="The port to bind to.")
@click.option("--cert", help="Specify a certificate file to use HTTPS.")
@click.option("--key", help="The key file to use when specifying a certificate.")
@click.option("--debugger/--no-debugger",
    default=None,
    help="Enable or disable the debugger. By default the debugger "
    "is active if debug is enabled.",
)
@click.pass_context
def run_ssl_command(
		ctx: Context,
		host: str,
		port: int,
		cert: str,
		key: str,
        **options: Any
    ) -> None:

	ssl_ctx = create_default_context(Purpose.CLIENT_AUTH)
	ssl_ctx.load_cert_chain(cert, key, app.secret_key)
	ctx.params["cert"] = ssl_ctx
	ctx.params.pop("key")

	ctx.forward(run_command)



@app.before_request
def app_before_request():
	_request_context.set(RequestContext())
	return authenticate()

@app.teardown_request
def app_teardown_request(err):
	rq = request_context
	if rq != None:
		try:
			del rq
			_request_context.set(None)
		except:
			logging.error(exc_info())

@app.route(ROOT_ENDPOINT, methods = ['GET'])
@authorize("guest")
def list_tarps():
	db_context = request_context.tarps_context

	tarp_list = db_context.select(order_by=TARPS_PROPS.TARP_NUMBER)

	selectors = []
	for id in range(env.max_selectors):
		selectors.append(Selector())

	sequence = []
	for id in range(env.max_orders):
		sequence.append(Order())

	empty_selection = Selection(selectors, sequence)
	return render_tarp_list(tarp_list, empty_selection)

@app.route(ROOT_ENDPOINT, methods = ['POST'])
@authorize("guest")
def list_tarp_by():
	db_context = request_context.tarps_context

	selectors = []
	for id in range(env.max_selectors):
		prop = request.form[f"select_by_{id}"]
		if prop != "None":
			value_list = request.form[f"select_value_{id}"].split()
			is_pattern = db_context.is_pattern_property(prop)
			selectors.append(Selector(prop, value_list, is_pattern))
		else:
			selectors.append(Selector())

	sequence = []
	for id in range(env.max_orders):
		prop = request.form[f"order_by_{id}"]
		if prop != "None":
			is_descending = request.form.__contains__(f"order_dir_{id}")
			sequence.append(Order(prop, is_descending))
		else:
			sequence.append(Order())

	selected_tarps = request.form["selected_numbers"]

	if selected_tarps != None:
		selected_numbers = [int(x) for x in selected_tarps.split(',')]
	else:
		selected_numbers = None

	selection = Selection(selectors, sequence, selected_numbers)
	tarp_list = db_context.select(selection)

	return render_tarp_list(tarp_list, selection)

def render_tarp_list(tarp_list, selection):
	return request_context.view_result("tarps_list.html.jinja", tarp_list=tarp_list, selection=selection, TARPS_PROPS=TARPS_PROPS)
