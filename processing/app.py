import connexion
import requests
import yaml
import json
import datetime
import logging
import logging.config
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open('app_conf_file', 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open('log_conf_file', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

path = '/data'
isExist = os.path.exists(path)
if not isExist:
    os.makedirs(path)
    create_table()

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def create_table():
    conn = sqlite3.connect('/data/data.sqlite')
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


def get_stats():

    logger.info("Request Has Started.")
    session = DB_SESSION()
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if stats:
        stats = stats.to_dict()
        logger.debug(".")
    else:
        session.close()
        return {"message": "error"}, 400

    session.close()
    logger.debug(f'{stats}')
    logger.info("Request Has Completed.")

    return stats, 200


def add_stat(stats):

    session = DB_SESSION()
    stt = Stats(stats['num_rr_readings'],
                stats['max_dist'],
                stats['max_price'],
                stats['num_sr_readings'],
                datetime.datetime.strptime(stats['last_updated'], "%Y-%m-%d %H:%M:%S"))
    session.add(stt)
    session.commit()
    session.close()
    logger.info('Database Updated')


def populate_stats():
    """ Periodically update stats """

    logger.info("Periodic Processing Started.")
    session = DB_SESSION()
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if stats:
        stats = stats.to_dict()
    else:
        stats = {
            'num_rr_readings': 0,
            'max_dist': 0,
            'max_price': 0,
            'num_sr_readings': 0,
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    rr_res = requests.get(app_config['eventstore1']['url'] + "?start_timestamp="+ stats['last_updated'] + "&end_timestamp="+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sr_res = requests.get(app_config['eventstore2']['url'] + "?start_timestamp="+ stats['last_updated'] + "&end_timestamp="+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    rr_data = rr_res.json()
    sr_data = sr_res.json()
    print(rr_data)
    print(sr_data)
    num_events = len(rr_data) + len(sr_data)
    if rr_res.status_code == 200 and sr_res.status_code == 200:
        logger.info(f'There are {num_events} events received')
        for event in rr_data:
            event_id = event['trace_id']
            logger.debug(f'Event_ID: {event_id}')
            stats['num_rr_readings'] += 1
            if event['distance'] > stats['max_dist']:
                stats['max_dist'] = event['distance']
            if event['price'] > stats['max_price']:
                stats['max_price'] = event['price']
        stats['num_sr_readings'] += stats['num_sr_readings'] + len(sr_data)
        stats['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        add_stat(stats)
        logger.debug(f'Stats Updated.')
        logger.info("Periodic Processing Ended.")

    else:
        logger.error(f'Not A Successful Request')


def init_scheduler():
    sched = BackgroundScheduler(timezone='America/Vancouver', daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS']='Content-Type'
app.add_api("./openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, debug=True)
