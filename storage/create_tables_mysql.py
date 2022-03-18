import mysql.connector
import yaml
import logging

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

db_conn = mysql.connector.connect(host=app_config['datastore']['hostname'],
                                  user=app_config['datastore']['user'],
                                  password=app_config['datastore']['password'],
                                  database=app_config['datastore']['db'],
                                  port=app_config['datastore']['port'])

# logger.info('Connecting to DB. Hostname:%s, port:%s' % (app_config['datastore']['hostname'], app_config[
# 'datastore']['port']))

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE ride_request
          (id INT NOT NULL AUTO_INCREMENT,
           customer_id VARCHAR(250) NOT NULL,
           distance DECIMAL(4,1) NOT NULL,
           price DECIMAL(6,2) NOT NULL,
           payment_method_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT ride_request_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE schedule_request
          (id INT NOT NULL AUTO_INCREMENT,
           customer_id VARCHAR(250) NOT NULL,
           date_time VARCHAR(250) NOT NULL,
           distance DECIMAL(4,1) NOT NULL,
           price DECIMAL(6,2) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT schedule_request_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
