from flask import Blueprint, request, jsonify
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login to receive JWT token
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
              password:
                type: string
            required:
              - username
              - password
    responses:
      200:
        description: Returns JWT token
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if data and data.get('username') == 'admin' and data.get('password') == 'password':
        token = jwt.encode({
            'user': data['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, 'your_secret_key', algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

