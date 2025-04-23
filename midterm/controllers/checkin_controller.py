from flask import Blueprint, request, jsonify
from dtos.checkin_dtos import CheckInDTO
from services.checkin_service import check_in, get_passenger_list
from auth.jwt_required import jwt_required

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/', methods=['POST'])
def do_checkin():
    """
Check in to flight
---
tags:
  - Check-in
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          flight_id:
            type: integer
          passenger_name:
            type: string
        required:
          - flight_id
          - passenger_name
responses:
  200:
    description: Check-in result
"""

    data = request.get_json()
    dto = CheckInDTO(**data)
    result = check_in(dto)
    return jsonify(result)

@checkin_bp.route('/<flight_id>/passengers', methods=['GET'])
@jwt_required
def passenger_list(flight_id):
    """
    Get list of checked-in passengers for a flight
    ---
    tags:
      - Check-In
    security:
      - BearerAuth: []
    parameters:
      - name: flight_id
        in: path
        type: string
        required: true
      - name: page
        in: query
        type: integer
      - name: pageSize
        in: query
        type: integer
    responses:
      200:
        description: List of passengers
      403:
        description: Unauthorized
    """
    ...

    page = int(request.args.get("page", 1))
    size = int(request.args.get("pageSize", 10))
    result = get_passenger_list(flight_id, page, size)
    return jsonify(result)
