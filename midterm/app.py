import os
from flask import Flask
from flasgger import Swagger
from controllers.flight_controller import flight_bp
from controllers.ticket_controller import ticket_bp
from controllers.checkin_controller import checkin_bp
from auth.auth_controller import auth_bp
from db import SessionLocal, init_db
from models.flight import Flight


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SWAGGER'] = {
    'title': 'Airline API',
    'uiversion': 3,
    'openapi': '3.0.2',
    'components': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        }
    },
    'security': [{'BearerAuth': []}]
}
swagger = Swagger(app)

app.register_blueprint(flight_bp, url_prefix='/api/v1/flights')
app.register_blueprint(ticket_bp, url_prefix='/api/v1/tickets')
app.register_blueprint(checkin_bp, url_prefix='/api/v1/checkin')
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

if __name__ == '__main__':
    DB_PATH = "data/airline.db"

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    app.run(debug=True)
