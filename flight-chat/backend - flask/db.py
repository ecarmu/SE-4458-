from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.flight import Flight
from models.ticket import Ticket
import datetime
import os

os.makedirs("data", exist_ok=True)

engine = create_engine('sqlite:///data/airline.db', echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

from db import engine, Base, SessionLocal
from models.flight import Flight

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # 🔄 Otomatik örnek uçuşlar ekle
    session = SessionLocal()
    try:
        if session.query(Flight).count() == 0:  # Eğer hiç uçuş yoksa
            flights = [
                Flight(from_airport="IST", to_airport="LON", date=datetime.date(2011, 11, 11), duration="2 hours", capacity=10, booked=0),
                Flight(from_airport="IZM", to_airport="MAD", date=datetime.date(2011, 11, 12), duration="3 hours", capacity=2, booked=0),
                Flight(from_airport="IZM", to_airport="LON", date=datetime.date(2011, 11, 13), duration="2.5 hours", capacity=5, booked=0),
                Flight(from_airport="LON", to_airport="IZM", date=datetime.date(2011, 11, 14), duration="2.5 hours", capacity=5, booked=0)

            ]
            session.add_all(flights)
            session.commit()
    finally:
        session.close()   
