import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE point
          ''')

conn.commit()
conn.close()
