import connexion
from connexion import NoContent
import json
import requests
import yaml
import logging
import logging.config
import uuid
import datetime
from pykafka import KafkaClient
import time
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

max_retry = app_config['connection']['maxretry']
current_retry = 0
while current_retry <= max_retry:
    logger.info("Trying to connect to kafka. Retry number %s" % current_retry)
    try:
        client = KafkaClient(hosts='{}:{}'.format(app_config['events']['hostname'], app_config['events']['port']))
        topic = client.topics[str.encode(app_config['events']['topic'])]
        break
    except:
        logger.error(f'Connection Failed!')
        time.sleep(app_config['sleep']['time'])
        current_retry += 1


def immediate_ride(body):
    body["trace_id"] = str(uuid.uuid4())

    msg = {"type": "eventride",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S "),
           "payload": body}
    msg_str = json.dumps(msg)
    producer = topic.get_sync_producer()
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Received event Ride with a trace id of %s ', body["trace_id"])
    logger.info('Returned event Ride response (id: %s) with status 201', body["trace_id"])

    return NoContent, 201


def scheduled_ride(body):
    body["trace_id"] = str(uuid.uuid4())

    msg = {"type": "eventschedule",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer = topic.get_sync_producer()
    producer.produce(msg_str.encode('utf-8'))

    logger.info('Received event Ride with a trace id of %s ', body["trace_id"])
    logger.info('Returned event Ride response (id: %s) with status 201', body["trace_id"])

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
