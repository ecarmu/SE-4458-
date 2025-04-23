from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    passenger_name = Column(String, nullable=False)
    seat_number = Column(String, nullable=True)
