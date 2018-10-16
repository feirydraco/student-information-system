from flask import Flask, url_for, render_template, g, request, redirect
import os
import sqlite3


app = Flask(__name__)
DATABASE = "data.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def change_db(query,args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
	student_list = query_db("SELECT * FROM student")
	return render_template("index.html", student_list=student_list)

@app.route('/create', methods=['GET', 'POST'])
def create():
	if request.method == "GET":
		return render_template("create.html",student=None)
	if request.method == "POST":
		student = request.form.to_dict()
		values = [student["USN"], student["Name"], student["Semester"], student["Age"], student["Section"], student["Class_ID"], student["Mentor"]]
		change_db("INSERT INTO Student VALUES (?, ?, ?, ?, ?, ?, ?)", values)
		return redirect(url_for("index"))

@app.route('/update/<int:salesman_id>', methods=['GET', 'POST'])
def update(salesman_id):
	if request.method == "GET":
		salesman = query_db("SELECT * FROM salesman WHERE salesman_id=?", [salesman_id], one=True)
		return render_template("update.html", salesman=salesman)
	if request.method == "POST":
		salesman = request.form.to_dict()
		values = [salesman["salesman_id"], salesman["name"], salesman["city"], salesman["commission"], salesman_id]
		change_db("UPDATE salesman SET salesman_id=?, name=?, city=?, commission=? WHERE salesman_id=?", values)
		return redirect(url_for("index"))

@app.route('/delete/<int:salesman_id>', methods=['GET', 'POST'])
def delete(salesman_id):
	if request.method == "GET":
		salesman = query_db("SELECT * FROM salesman WHERE salesman_id=?", [salesman_id], one=True)
		return render_template("delete.html", salesman=salesman)
	if request.method == "POST":
		change_db("DELETE FROM salesman where salesman_id=?", [salesman_id])
		return redirect(url_for("index"))

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5010, debug=True)
