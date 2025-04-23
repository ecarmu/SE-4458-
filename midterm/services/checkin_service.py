from db import SessionLocal
from models.ticket import Ticket

def check_in(dto):
    session = SessionLocal()
    try:
        # 1. İlgili bileti bul
        ticket = session.query(Ticket).filter_by(
            flight_id=dto.flight_id,
            passenger_name=dto.passenger_name
        ).first()

        if not ticket:
            return {"status": "error", "message": "Ticket not found"}

        # 2. Zaten check-in yapılmış mı?
        if ticket.seat_number:
            return {"status": "already checked in", "seat_number": ticket.seat_number}

        # 3. Bu uçuşta kullanılan koltukları al
        used_seats = session.query(Ticket.seat_number).filter(
            Ticket.flight_id == dto.flight_id,
            Ticket.seat_number.isnot(None)
        ).all()

        used_set = {s[0] for s in used_seats}

        # 4. İlk boş koltuğu bul
        seat_number = None
        for i in range(1, 150):  # örneğin 1A, 2A, ..., 149A
            candidate = f"{i}A"
            if candidate not in used_set:
                seat_number = candidate
                break

        if not seat_number:
            return {"status": "error", "message": "No available seats"}

        # 5. Koltuk numarasını ata ve kaydet
        ticket.seat_number = seat_number
        session.commit()

        return {"status": "checked in", "seat_number": seat_number}

    except Exception as e:
        session.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        session.close()



from db import SessionLocal
from models.ticket import Ticket

def get_passenger_list(flight_id, page, size):
    session = SessionLocal()
    try:
        query = session.query(Ticket).filter(
            Ticket.flight_id == flight_id
        ).order_by(Ticket.seat_number)

        total = query.count()
        passengers = query.offset((page - 1) * size).limit(size).all()

        return {
            "total": total,
            "page": page,
            "size": size,
            "passengers": [
                {
                    "name": t.passenger_name,
                    "seat": t.seat_number
                } for t in passengers
            ]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        session.close()

