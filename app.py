from environment import Environment
from flask import Flask
from flask import render_template, request, session, redirect, url_for
from auth_context import AuthenticationContext
from tarps_context import TarpsContext
from tarps_context import TARPS_PROPS
from user_context import USER_PROPS
from entities import Selector
from entities import Order
from entities import Selection
from user_context import UserContext
from contextvars import ContextVar
from werkzeug.local import LocalProxy

env = Environment()
env.init_logging()
env.log()
app = Flask(__name__)
app.secret_key = env.get_secret_key()

if __name__ == '__main__':
	app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)

_auth_context = ContextVar("auth_context")
auth_context = LocalProxy(_auth_context)

@app.before_request
def authenticate():
	if not request.path.startswith("/static"):
		auth_context = AuthenticationContext()
		if request.path == "/login":
			auth_context.user = None 
		elif USER_PROPS.USER_NAME in session:
			user_context = UserContext(env.db_users)
			auth_context.user = user_context.get_user_by_name(session[USER_PROPS.USER_NAME])		
		else:
			auth_context.user = None
			return redirect(url_for("login"))		




@app.route("/login", methods = ['GET', 'POST'])
def login():
	if request.method == "GET" or request.form[USER_PROPS.USER_NAME] == None:
		return render_template("login.html.jinja", USER_PROPS=USER_PROPS)
	else:
		user_name = request.form[USER_PROPS.USER_NAME]
		redir = None
		user_context = UserContext(env.db_users)
		user = user_context.get_user_by_name(user_name)		
		if user == None:
			redir = "login"
		else:
			if user.check_pwd(request.form[USER_PROPS.USER_PASSWORD]):
				session[USER_PROPS.USER_NAME] = user.name
				redir = "/"
			else:
				redir = "login"

		redirect(url_for(redir))

@app.route("/logout", methods = ['GET'])
def logout():
	session.clear()

@app.route("/", methods = ['GET'])
def list_tarps():
	db_context = TarpsContext(env.db_tarps)

	tarp_list = db_context.select(order_by=TARPS_PROPS.TARP_NUMBER)

	selectors = []
	for id in range(env.max_selectors):
		selectors.append(Selector())

	sequence = []
	for id in range(env.max_orders):
		sequence.append(Order())

	empty_selection = Selection(selectors, sequence)
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list, selection=empty_selection, TARPS_PROPS=TARPS_PROPS)
	
@app.route("/", methods = ['POST'])
def list_tarp_by():
	db_context = TarpsContext(env.db_tarps)

	selectors = []
	for id in range(env.max_selectors):
		prop = request.form[f"select_by_{id}"]
		if prop != "None":
			value_list = split_values(request.form[f"select_value_{id}"])
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

	selection = Selection(selectors, sequence)
		
	tarp_list = db_context.select(selection)
		
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list, selection=selection, TARPS_PROPS=TARPS_PROPS)

def split_values(text):
	return text.split()