from flask import Flask
from flask import render_template
from flask import request
from db_context import DbContext
from db_context import PROPS

app = Flask(__name__)

# TODO: Get rid of hard-wired database path
db_path = "D:\\Gamer I5\\Documents\\Projects\\Planenprogramm\\Planenprogramm\\data\\tarps.sqlite"

if __name__ == '__main__':
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)


@app.route("/", methods = ['GET'])
def list_tarps():
	db_context = DbContext(db_path)

	tarp_list = db_context.select(order_by=PROPS.TARP_NUMBER)
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list)
	
@app.route("/", methods = ['POST'])
def list_tarp_by():
	db_context = DbContext(db_path)

	select_by = request.form["select_by"]
	select_value = request.form["select_value"]
	order_by = request.form["order_by"]

	value_list = split_values(select_value)

	if select_by == "none":
		tarp_list = db_context.select(order_by=order_by)
	elif select_by == PROPS.TARP_NUMBER:
		tarp_list = db_context.select_by_numbers(value_list, order_by)
	elif select_by == PROPS.TYPE_NAME:
		tarp_list = db_context.select_by_type(value_list, order_by)
	elif select_by == PROPS.CAT_NAME:
		tarp_list = db_context.select_by_category(value_list, order_by)
	elif select_by == PROPS.DMG_CODE:
		tarp_list = db_context.select_by_damage(value_list, order_by)
	else:
		raise Exception(f"Unexpected selection type '{select_by}'")
		
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list, select_by=select_by, select_value=select_value, order_by=order_by, PROPS=PROPS)

def split_values(text):
	return text.split()