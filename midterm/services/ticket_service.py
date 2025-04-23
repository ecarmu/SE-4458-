from db import SessionLocal
from models.flight import Flight
from models.ticket import Ticket

def buy_ticket(dto):
    session = SessionLocal()
    try:
        flight = session.query(Flight).filter(Flight.id == dto.flight_id).first()
        if not flight:
            return {"status": "error", "message": "Flight not found"}

        if flight.booked >= flight.capacity:
            return {"status": "error", "message": "Flight is sold out"}

        # Create ticket WITHOUT seat number
        ticket = Ticket(
            flight_id=flight.id,
            passenger_name=dto.passenger_name,
            seat_number=None  # ❗ Check-in sırasında atanacak
        )
        session.add(ticket)

        # Increment booked count on flight
        flight.booked += 1
        session.commit()

        return {
            "status": "success",
            "ticket_number": f"TK{ticket.id:04d}"
        }

    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        session.close()