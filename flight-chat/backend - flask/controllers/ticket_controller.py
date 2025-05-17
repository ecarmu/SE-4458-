from flask import Blueprint, request, jsonify
from dtos.ticket_dtos import BuyTicketDTO
from services.ticket_service import buy_ticket
from auth.jwt_required import jwt_required

ticket_bp = Blueprint('tickets', __name__)

@ticket_bp.route('/buy', methods=['POST'])
#@jwt_required
def buy():
    """
    Buy a ticket for a flight
    ---
    tags:
      - Tickets
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              flight_id:
                type: string
              passenger_name:
                type: string
            required:
              - flight_id
              - passenger_name
    responses:
      200:
        description: Ticket purchased
    """
    ...

    data = request.get_json()
    dto = BuyTicketDTO(**data)
    result = buy_ticket(dto)
    return jsonify(result)
