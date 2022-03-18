import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE ride_request
          (id INTEGER PRIMARY KEY ASC, 
           customer_id VARCHAR(250) NOT NULL,
           distance DECIMAL(4,1) NOT NULL,
           price DECIMAL(6,2) NOT NULL,
           payment_method_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE schedule_request
          (id INTEGER PRIMARY KEY ASC, 
           customer_id VARCHAR(250) NOT NULL,
           date_time VARCHAR(250) NOT NULL,
           distance DECIMAL(4,1) NOT NULL,
           price DECIMAL(6,2) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
