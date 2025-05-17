from sqlalchemy import Column, Integer, String, Date
from .base import Base

class Flight(Base):
    __tablename__ = 'flights'

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_airport = Column(String, nullable=False)
    to_airport = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    duration = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    booked = Column(Integer, default=0)
