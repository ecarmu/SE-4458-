from flask import Blueprint, request, jsonify, abort
from services.flight_service import add_flight
from dtos.flight_dtos import AddFlightDTO
from auth.jwt_required import jwt_required
from datetime import datetime
from flasgger.utils import swag_from
from services.flight_service import query_flights


flight_bp = Blueprint('flights', __name__)

@flight_bp.route('/', methods=['POST'])
@jwt_required
def create_flight():
    """
    Add a new flight
    ---
    tags:
      - Flights
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              from_airport:
                type: string
              to_airport:
                type: string
              date:
                type: string
                format: date
              duration:
                type: string
              capacity:
                type: integer
            required:
              - from_airport
              - to_airport
              - date
              - duration
              - capacity
    responses:
      200:
        description: Flight added successfully
      403:
        description: Unauthorized
    """
    ...

    data = request.get_json()
    data['date'] = datetime.strptime(data['date'], "%Y-%m-%d").date()

    dto = AddFlightDTO(**data)
    result = add_flight(dto)
    return jsonify(result)

@flight_bp.route('/search', methods=['GET'])
@swag_from({
    'tags': ['Flights'],
    'parameters': [
        {
            'name': 'from_airport',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        {
            'name': 'to_airport',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        {
            'name': 'min_seats',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'page_size',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'round_trip',
            'in': 'query',
            'type': 'boolean',
            'required': False
        },
        {
            'name': 'date_from',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Outbound flight date (format: YYYY-MM-DD)'
        },
        {
            'name': 'date_to',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Return flight date (format: YYYY-MM-DD)'
        }
    ],
    'responses': {
        200: {
            'description': 'Outbound and optionally return flights'
        },
        400: {
            'description': 'Missing required date_from or date_to parameter'
        }
    }
})
def search_flights():
    from_airport = request.args.get("from_airport")
    to_airport = request.args.get("to_airport")
    min_seats = int(request.args.get("min_seats", 1))
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    round_trip = request.args.get("round_trip", "false").lower() == "true"

    # Zorunlu tarih parametreleri
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    if not date_from_str or not date_to_str:
        abort(400, description="Both 'date_from' and 'date_to' are required.")

    # Tarihleri parse et
    try:
        date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
    except ValueError:
        abort(400, description="Dates must be in format YYYY-MM-DD.")

    result = query_flights(
        from_airport=from_airport,
        to_airport=to_airport,
        min_seats=min_seats,
        page=page,
        page_size=page_size,
        round_trip=round_trip,
        date_from=date_from,
        date_to=date_to
    )

    return jsonify(result)