from functools import wraps
from flask import request, jsonify
import jwt

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid or expired'}), 403
        return func(*args, **kwargs)
    return wrapper
