from sqlalchemy import Column, Integer, String, Float, DateTime
from base import Base
import datetime
import uuid


class RideRequest(Base):
    """ Requests for immediate rides """

    __tablename__ = "ride_request"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(250), nullable=False)
    distance = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    payment_method_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, customer_id, distance, price, payment_method_id, trace_id):
        """ Initializes a ride request reading """
        self.customer_id = customer_id
        self.distance = distance
        self.price = price
        self.payment_method_id = payment_method_id
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a ride request reading """
        dict = {}
        dict['id'] = self.id
        dict['customer_id'] = self.customer_id
        dict['distance'] = self.distance
        dict['price'] = self.price
        dict['payment_method_id'] = self.payment_method_id
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
