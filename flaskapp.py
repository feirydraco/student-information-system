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

# def format_datetime(value, format='medium'):
# 	if format == 'full':
# 		format="EEEE, d. MMMM y 'at' HH:mm"
# 	elif format == 'medium':
# 		format="EE dd.MM.y HH:mm"
# 	return babel.dates.format_datetime(value, format)
#
# app.jinja_env.filters['datetime'] = format_datetime

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.route("/")
def index_student():
	student_list = query_db("SELECT * FROM student")
	return render_template("index_student.html", student_list=student_list)

@app.route("/teachers")
def index_teacher():
	teacher_list = query_db("SELECT * FROM teacher")
	return render_template("index_teacher.html", teacher_list=teacher_list)

@app.route('/create', methods=['GET', 'POST'])
def create():
	if request.method == "GET":
		return render_template("create.html",student=None)
	if request.method == "POST":
		student = request.form.to_dict()
		values = [student["USN"], student["Name"], student["Semester"], student["Age"], student["Section"], student["Class_ID"], student["Mentor"]]
		change_db("INSERT INTO Student VALUES (?, ?, ?, ?, ?, ?, ?)", values)
		return redirect(url_for("index"))

@app.route('/update/<string:USN>', methods=['GET', 'POST'])
def update(USN):
	if request.method == "GET":
		student = query_db("SELECT * FROM Student WHERE USN=?", [USN], one=True)
		print(student["Mentor"])
		return render_template("update.html", student=student)
	if request.method == "POST":
		student = request.form.to_dict()

		#TODO
		print(student["Mentor"])

		values = [student["USN"], student["Name"], student["Semester"], student["dob"], student["Section"], student["Class_ID"], student["Mentor"], USN]
		change_db("UPDATE Student SET USN=?, Name=?, Semester=?, dob=?, Section=?, Class_ID=?, Mentor=? WHERE USN=?", values)

		return redirect(url_for("index"))

@app.route('/update_teacher/<string:Teacher_ID>', methods=['GET', 'POST'])
def update_teacher(Teacher_ID):
	if request.method == "GET":
		teacher = query_db("SELECT * FROM teacher WHERE Teacher_ID=?", [Teacher_ID], one=True)
		return render_template("update_teacher.html", teacher=teacher)
	if request.method == "POST":
		teacher = request.form.to_dict()
		values = [teacher["Teacher_ID"], teacher["Name"], teacher["Class_ID"], teacher["Subject"], Teacher_ID]
		change_db("UPDATE Teacher SET Teacher_ID=?, Name=?, Class_ID=?, Sub=? WHERE Teacher_ID=?", values)

		return redirect(url_for("index_teacher"))

@app.route('/delete/<string:USN>', methods=['GET', 'POST'])
def delete(USN):
	if request.method == "GET":
		student = query_db("SELECT * FROM student WHERE USN=?", [USN], one=True)
		return render_template("delete.html", student=student)
	if request.method == "POST":
		change_db("DELETE FROM student where USN=?", [USN])
		return redirect(url_for("index"))

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5010, debug=True)
