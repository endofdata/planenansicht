import selectors
from flask import Flask
from flask import render_template
from flask import request
from db_context import DbContext
from db_context import PROPS
from entities import Selector
from entities import Order
from entities import Selection

app = Flask(__name__)

# TODO: Get rid of hard-wired database path
DB_PATH = "D:\\Gamer I5\\Documents\\Projects\\Planenprogramm\\Planenprogramm\\data\\tarps.sqlite"
MAX_SELECTORS = 3
MAX_SEQUENCE = 2

if __name__ == '__main__':
    app.run(use_debugger=False, use_reloader=False, passthrough_errors=True)


@app.route("/", methods = ['GET'])
def list_tarps():
	db_context = DbContext(DB_PATH)

	tarp_list = db_context.select(order_by=PROPS.TARP_NUMBER)

	selectors = []
	for id in range(MAX_SELECTORS):
		prop = None
		value_list = None
		is_pattern = False
		selectors.append(Selector(prop, value_list, is_pattern))

	sequence = []
	for id in range(MAX_SEQUENCE):
		prop = None
		sequence.append(Order(prop, False))

	empty_selection = Selection(selectors, sequence)
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list, selection=empty_selection, PROPS=PROPS)
	
@app.route("/", methods = ['POST'])
def list_tarp_by():
	db_context = DbContext(DB_PATH)

	selectors = []
	for id in range(MAX_SELECTORS):
		prop = request.form[f"select_by_{id}"]
		if prop != "None":
			value_list = split_values(request.form[f"select_value_{id}"])
			is_pattern = db_context.is_pattern_property(prop)
			selectors.append(Selector(prop, value_list, is_pattern))
		else:
			selectors.append(Selector())

	sequence = []
	for id in range(MAX_SEQUENCE):
		prop = request.form[f"order_by_{id}"]
		if prop != "None":
			is_descending = request.form.__contains__(f"order_dir_{id}")
			sequence.append(Order(prop, is_descending))
		else:
			sequence.append(Order())

	selection = Selection(selectors, sequence)
		
	tarp_list = db_context.select(selection)
		
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list, selection=selection, PROPS=PROPS)

def split_values(text):
	return text.split()