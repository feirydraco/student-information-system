import sqlite3
import re
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None



def select_all_content(conn, tableName, file):
    cur = conn.cursor()
    cur.execute("Select Name from "+ tableName);
    rows = cur.fetchall()
    for row in rows:
        val = str(row)
        val = val.strip('(\'')
        val = val.strip('\',)')
        print(val)
        file.write("\"" + val + "\": \"" +  tableName.lower() + "\",")


def main():
    #Change this path according to your File System
    database = "/home/vivek/Desktop/flask-demo-master/data.db"
    f = open("Search.json","w+")

    f.write("{")
    conn = create_connection(database)
    with conn:
        select_all_content(conn, "Teacher", f)
        select_all_content(conn, "Student", f)
    f.write("}")
    f.close()


if __name__ == '__main__':
    main()

