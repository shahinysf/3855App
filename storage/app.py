import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from base import Base
from ride_request import RideRequest
from schedule_request import ScheduleRequest
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

user = app_config['datastore']['user']
passwd = app_config['datastore']['password']
host = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}', pool_size=20, max_overflow=0)


Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def immediate_ride(body):
    session = DB_SESSION()

    rr = RideRequest(body['customer_id'],
                     body['distance'],
                     body['price'],
                     body['payment_method_id'],
                     body['trace_id'])

    session.add(rr)

    session.commit()
    session.close()
    logger.debug('Stored event Ride request with a trace id of %s ', body["trace_id"])

    return NoContent, 201


def scheduled_ride(body):
    session = DB_SESSION()

    sr = ScheduleRequest(body['customer_id'],
                         body['date_time'],
                         body['distance'],
                         body['price'],
                         body['trace_id'])

    session.add(sr)

    session.commit()
    session.close()
    logger.debug('Stored event Schedule request with a trace id of %s ', body["trace_id"])

    return NoContent, 201


def get_ride_request_readings(start_timestamp, end_timestamp):

    """Gets new ride request readings after the timestamp"""

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")
    readings = session.query(RideRequest).filter(and_(RideRequest.date_created >= start_timestamp_datetime, 
                                                RideRequest.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
        session.close()
        logger.info("Query for Ride Request readings after %s returns %d results" %
                    (timestamp, len(results_list)))
    return results_list, 200


def get_schedule_request_readings(timestamp):

    """Gets new schedule request readings after the timestamp"""

    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")
    readings = session.query(ScheduleRequest).filter(and_(ScheduleRequest.date_created >= start_timestamp_datetime,
                                                         ScheduleRequest.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
        session.close()
        logger.info("Query for Schedule Request readings after %s returns %d results" %
                    (timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    max_retry = app_config['connection']['maxretry']
    current_retry = 0
    while current_retry <= max_retry:
        logger.info("Trying to connect to kafka. Retry number %s" % current_retry)
        try:
            client = KafkaClient(hosts='{}:{}'.format(app_config['events']['hostname'], app_config['events']['port']))
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.error(f'Connection Failed!')
            time.sleep(app_config['sleep']['time'])
            current_retry += 1

    # Create a "consume" on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        # Store the event1 (i.e., the payload) to the DB
        if msg["type"] == "eventride":
            immediate_ride(payload)

        # Store the event2 (i.e., the payload) to the DB
        elif msg["type"] == "eventschedule":
            scheduled_ride(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=8090, debug=True)
    logger.info(f'Connecting to DB. Hostname:{host}, port:{port}')


