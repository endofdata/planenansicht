from flask import Flask
from flask import render_template
from db_context import DbContext

app = Flask(__name__)

db_path = "D:\\Gamer I5\\Documents\\Projects\\Planenprogramm\\Planenprogramm\\data\\tarps.sqlite"


@app.route("/")
def list_tarps():

	db_context = DbContext(db_path)

	tarp_list = db_context.select_by_damage(['Ö', 'K'])
	return render_template("tarps_list.html.jinja", tarp_list=tarp_list)
	

