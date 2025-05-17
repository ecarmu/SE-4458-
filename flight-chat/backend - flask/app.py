import os
from flask import Flask
from flasgger import Swagger
from controllers.flight_controller import flight_bp
from controllers.ticket_controller import ticket_bp
from controllers.checkin_controller import checkin_bp
from auth.auth_controller import auth_bp
from db import SessionLocal, init_db
from models.flight import Flight

from agent import agent_bp
from flask_cors import CORS

from flask import Flask
from flask_socketio import SocketIO
from agent import run_agent_logic

import openai

openai.api_key = "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"

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app,
                        cors_allowed_origins="*",
                        async_mode='threading',
                        logger=True, engineio_logger=True)

app.config['API_BASE'] = os.getenv('API_BASE')
app.config['SERVER_URL'] = 'http://127.0.0.1:5000'
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
app.register_blueprint(agent_bp)

from flask_socketio import SocketIO, emit
from agent import run_agent_logic

import traceback

@socketio.on('user_message')
def on_user_message(msg):
    user_text = msg.get('text', '')
    try:
        reply, data = run_agent_logic(user_text)
    except Exception as e:
        # log the full stack to your console
        print("⚠️ Error in run_agent_logic:", e)
        traceback.print_exc()
        # send an error back rather than hanging
        emit('bot_message', {
            'reply': "⚠️ Internal error handling your request. Please try again.",
            'data': {}
        })
    else:
        emit('bot_message', {'reply': reply, 'data': data})


if __name__ == '__main__':
    DB_PATH = "data/airline.db"

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    #app.run(debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, allow_unsafe_werkzeug=True))
