from sqlalchemy import Column, Integer, String, Float, DateTime
from base import Base
import datetime
import uuid


class ScheduleRequest(Base):
    """ Requests for scheduled rides """

    __tablename__ = "schedule_request"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    date_time = Column(String(250), nullable=False)
    distance = Column(Float(100), nullable=False)
    price = Column(Float, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, customer_id, date_time, distance, price, trace_id):
        """ Initializes a heart rate reading """
        self.customer_id = customer_id
        self.date_time = date_time
        self.distance = distance
        self.price = price
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['date_time'] = self.date_time
        dict['distance'] = self.distance
        dict['price'] = self.price
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
