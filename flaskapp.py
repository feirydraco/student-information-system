from flask import Flask, url_for, render_template, g, request, redirect, flash, session, abort
from flask_login import LoginManager
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
import sqlite3
from urllib.parse import unquote

app = Flask(__name__)
DATABASE = "data.db"
# Config
app.config.from_object(__name__)

ID = None


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


def change_db(query, args=()):
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
    if not session.get('logged_in'):
        return login()
    else:
        return render_template("index.html", id=ID)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html", error=False)
    if request.method == 'POST':
        try:
            password = request.form['password']
            teacher_id = int(request.form['teacher_id'])
            print(password, teacher_id)
        except ValueError:
            return render_template("login.html", error=True)

        teacher = query_db("SELECT * FROM Teacher \
                                WHERE teacher_id = ?", [teacher_id], one=True)
        if teacher is None:
            return render_template("login.html", error=True)
            # TODO
        if teacher["password"] == password:
            session['logged_in'] = True
            global ID
            ID = teacher_id
            return index()
        else:
            return render_template("login.html", error=True)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/view', methods=['GET', 'POST'])
def view():
    global ID
    teacher = query_db("SELECT * FROM Teacher \
                         WHERE teacher_id=?", [ID], one=True)
    student_list = query_db("SELECT * FROM Student")
    if request.method == 'GET':
        if not session.get('logged_in'):
            return login()
        else:

            print(teacher)
            return render_template("user.html", id=ID, teacher=teacher, error=None, student_list=student_list)
    if request.method == 'POST':
        old = request.form['oldPassword']
        new = request.form['newPassword']

        if teacher['password'] == old:
            change_db("UPDATE Teacher SET password = ? WHERE teacher_id = ?", (new, ID))
            return render_template("user.html", id=ID, teacher=teacher, changed=True, student_list=student_list)
        else:
            return render_template("user.html", id=ID, teacher=teacher, error=True, student_list=student_list)

@app.route('/teachers', methods=['GET', 'POST'])
def teachers():
    global ID
    if request.method == 'GET':
        pass

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=5000, debug=True)
