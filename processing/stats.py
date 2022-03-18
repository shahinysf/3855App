from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_rr_readings = Column(Integer, nullable=False)
    max_dist = Column(Integer, nullable=False)
    max_price = Column(Integer, nullable=True)
    num_sr_readings = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_rr_readings, max_dist, max_price, num_sr_readings,
                 last_updated):
        """ Initializes a processing statistics objet """
        self.num_rr_readings = num_rr_readings
        self.max_dist = max_dist
        self.max_price = max_price
        self.num_sr_readings = num_sr_readings
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_rr_readings'] = self.num_rr_readings
        dict['max_dist'] = self.max_dist
        dict['max_price'] = self.max_price
        dict['num_sr_readings'] = self.num_sr_readings
        dict['last_updated'] = self.last_updated.strftime('%Y-%m-%d %H:%M:%S')

        return dict
