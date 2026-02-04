import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT title, type FROM content")
print(cursor.fetchall())

conn.close()
