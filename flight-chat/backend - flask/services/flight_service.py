from db import SessionLocal
from models.flight import Flight
from datetime import datetime

def add_flight(dto):
    session = SessionLocal()
    try:
        new_flight = Flight(
            from_airport=dto.from_airport,
            to_airport=dto.to_airport,
            date=dto.date,  # datetime.date object
            duration=dto.duration,
            capacity=dto.capacity,
            booked=0
        )

        session.add(new_flight)
        session.flush()  # ⬅️ get ID before commit
        flight_id = new_flight.id

        session.commit()

        return {
            "status": "success",
            "message": f"Flight from {dto.from_airport} to {dto.to_airport} on {dto.date} added.",
            "flight_id": flight_id
        }

    except Exception as e:
        session.rollback()
        print("❌ Add flight failed:", str(e))  # terminal log
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        session.close()

def query_flights(from_airport=None, to_airport=None, min_seats=1, page=1, page_size=10, round_trip=True, date_from=None, date_to=None):
    session = SessionLocal()
    try:
        # OUTBOUND flights (from → to)
        outbound_query = session.query(Flight).filter(
            Flight.capacity - Flight.booked >= min_seats,
            Flight.date.between(date_from, date_to)
        )
        if from_airport:
            outbound_query = outbound_query.filter(Flight.from_airport == from_airport)
        if to_airport:
            outbound_query = outbound_query.filter(Flight.to_airport == to_airport)

        outbound_flights = outbound_query.offset((page - 1) * page_size).limit(page_size).all()

        result = {
            "departure": [
                {
                    "flight_id": f.id,
                    "from": f.from_airport,
                    "to": f.to_airport,
                    "date": f.date,
                    "duration": f.duration,
                    "seats_left": f.capacity - f.booked
                } for f in outbound_flights if f is not None
            ]
        }

        for f in outbound_flights:
            if f is None:
                print("❌ Uçuş sonucu None geldi!")


        # RETURN flights (to → from)
        if round_trip:
            return_query = session.query(Flight).filter(
                Flight.capacity - Flight.booked >= min_seats,
                Flight.from_airport == to_airport,
                Flight.to_airport == from_airport,
                Flight.date.between(date_from, date_to)
            )

            return_flights = return_query.offset((page - 1) * page_size).limit(page_size).all()

            result["arrival"] = [
                {
                    "flight_id": f.id,
                    "from": f.from_airport,
                    "to": f.to_airport,
                    "date": f.date,
                    "duration": f.duration,
                    "seats_left": f.capacity - f.booked
                } for f in return_flights if f is not None
            ]

        return result
    finally:
        session.close()
