import sqlite3

conn = sqlite3.connect('data/data.sqlite')
c = conn.cursor()
c.execute(''' 
          CREATE TABLE stats 
          (id INTEGER PRIMARY KEY ASC, 
          num_rr_readings INTEGER NOT NULL, 
          max_dist INTEGER NOT NULL, 
          max_price INTEGER NOT NULL, 
          num_sr_readings INTEGER NOT NULL, 
          last_updated VARCHAR(100) NOT NULL) 
          ''')
conn.commit()
conn.close()
