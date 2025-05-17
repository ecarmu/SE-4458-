# agent.py
import os, json, requests, openai
from flask import Blueprint, request, jsonify, current_app
from openai import RateLimitError
from datetime import datetime, date
from requests.exceptions import HTTPError
#from app import socketio

agent_bp = Blueprint('agent', __name__)


# Load your OpenAI key from the Flask config (set via env-vars)

def run_agent_logic(user_text: str):
    #user_text = request.json.get('text', '')
    api_resp = {} 

    # 1) Build the messages payload for ChatGPT
    messages = [
        {
            "role": "system",
            "content": (
                "You are a flight-booking assistant. "
                "Parse the user’s message and return ONLY JSON with these keys:\n"
                "• intent: one of QUERY_FLIGHT, BUY_TICKET, or CHECK_IN\n"
                "The following are for QUERY_FLIGHT:"
                "• origin: IATA code of departure airport\n"
                "• destination: IATA code of arrival airport\n"
                "• date_from: date in YYYY-MM-DD format\n"
                "• date_to: date in YYYY-MM-DD format (same as date_from if single-day search)\n"
                "• min_seats: seats_left of the flights should be more than min_seats\n"
                "• page: amount of each page flights are displayed\n"
                "• page_size: amount of flights each page has\n"
                "• round_trip: if a user requests round-trip origin and destination can be both like that or vice versa\n"
                "The following are for BUY_TICKET and CHECK_IN:"
                "• flight_id: the id of the flight"
                "• pasenger_name: the name of the passenger"


                "Examples only for illustration; do NOT apply them to the user’s message."
            )
        },
        {"role": "user", "content": user_text}
    ]

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    except RateLimitError:
        f"⚠️ Sorry, I'm a bit overwhelmed right now. Please try again in a minute!", {}


    # Parse ChatGPT's JSON
    parsed = resp.choices[0].message.content.strip()
    try:
        parsed_json = json.loads(parsed)
    except json.JSONDecodeError:
        current_app.logger.error("JSON decode error, raw content was: %r", parsed)
        return f"⚠️ Sorry, I couldn’t understand the assistant’s response. Could you try again?", {}

    intent = parsed_json.get('intent')
    if intent not in ('QUERY_FLIGHT','BUY_TICKET','CHECK_IN'):
        current_app.logger.error("Unexpected intent: %r", parsed_json)
        return f"⚠️ I got an unexpected intent back. Please try rephrasing.", {}    # Normalize single-date into date_from/date_to
    if 'date' in parsed_json:
        parsed_json['date_from'] = parsed_json.pop('date')
        parsed_json['date_to'] = parsed_json['date_from']

    # Set defaults for date_from and date_to if missing
    default_from = date.min.isoformat()  # '0001-01-01'
    default_to = date.max.isoformat()    # '9999-12-31'
    date_from = parsed_json.get('date_from') or default_from
    date_to = parsed_json.get('date_to') or default_to

    try:
        base = request.url_root.rstrip('/')
    except RuntimeError:
        # no HTTP request context (e.g. SocketIO)
        base = current_app.config.get('SERVER_URL', 'http://localhost:5000')
    # Route to appropriate API based on intent
    if intent == 'QUERY_FLIGHT':
        params = {
            'from_airport': parsed_json.get('origin'),
            'to_airport': parsed_json.get('destination'),
            'date_from': date_from,
            'date_to': date_to,
            'min_seats': parsed_json.get('min_seats'),
            'page': parsed_json.get('page'),
            'page_size': parsed_json.get('page_size'),
            'round_trip': parsed_json.get('round_trip'),
        }
        print("➡️ Querying flights with:", params)
        print("➡️ API base URL:", base)

        try:
            resp_api = requests.get(f"{base}/api/v1/flights/search", params=params)
            resp_api.raise_for_status()
            api_resp = resp_api.json()
            #print("resp_api: " + resp_api + " api_resp: " + api_resp)
        except Exception as e:
            print("❌ Error calling /api/v1/flights/search:", e)
            return f"⚠️ Error fetching flight data from the API.", {}
        #print("resp_api: " + resp_api + " api_resp: " + api_resp)
        departures = api_resp.get('departure', [])
        arrivals = api_resp.get('arrival', [])
        if not departures:
            text = "Sorry, I couldn’t find any flights."
        else:
            print("c")
            lines = [
                f"🛫 Flight {f['flight_id']} from {f['from']} to {f['to']} on {f['date']} ({f['duration']})"
                for f in departures
            ]

            # two newlines after header, and newline at end
            text = "Here are the outbound flights:\n\n" \
                + "\n".join(lines) \
                + "\n"
            if arrivals:
                ret_lines = [
                    f"🛬 Flight {f['flight_id']} returning from {f['from']} to {f['to']} on {f['date']}"
                    for f in arrivals
                ]
                text += "\n\nAnd the return flights:\n" + "\n".join(ret_lines)
        return text, api_resp
    elif intent == 'BUY_TICKET':
        payload = {
            'flight_id':     parsed_json.get('flight_id'),
            'passenger_name':parsed_json.get('passenger_name')
        }
        if not payload['flight_id'] or not payload['passenger_name']:
            return "🚫 Please specify both flight ID and passenger name for buying ticket.", {}
        resp_api = requests.post(f"{base}/api/v1/tickets/buy", json=payload)
        try:
            resp_api.raise_for_status()
            api_resp = resp_api.json()
        except HTTPError as e:
            # Network / 5xx errors
            return f"⚠️ Unable to reach ticket service for flight {payload['flight_id']}. Please try again later.", {}
        # Application-level error (e.g. flight not found)
        if api_resp.get('status') == 'error':
            err = api_resp.get('message', 'Ticket purchase failed.')
            return f"🚫 {err}", api_resp

        # Success
        confirmation = api_resp.get('confirmation_number', '')
        text = f"🎫✅ Ticket purchase successful for {payload['passenger_name']} on flight {payload['flight_id']}."
        if confirmation:
            text += f" Confirmation number: {confirmation}."
        return text, api_resp

    elif intent == 'CHECK_IN':
        payload = {
            'flight_id':      parsed_json.get('flight_id'),
            'passenger_name': parsed_json.get('passenger_name')
        }
        if not payload['flight_id'] or not payload['passenger_name']:
            return "🚫 Please specify both flight ID and passenger name for check-in.", {}
        resp_api = requests.post(f"{base}/api/v1/checkin", json=payload)
        try:
            resp_api.raise_for_status()
            api_resp = resp_api.json()
        except HTTPError:
            # network / server-side error
           return f"⚠️ Unable to reach check-in service for flight {payload['flight_id']}. Please try again later.", {}
        except (ValueError, json.JSONDecodeError):
            # got a non-JSON response
            return "⚠️ Received an unexpected response from the check-in service. Please try again later.", {}

        if api_resp.get('status') == 'error':
            err = api_resp.get('message', 'Check-in failed.')
            return f"🚫 {err}", api_resp

        seat = api_resp.get('seat_number', '')
        text = f"✅ Check-in successful for {payload['passenger_name']} on flight {payload['flight_id']}."
        if seat:
            text += f" Your seat: {seat}."
        return text, api_resp

    # Fallback if intent is unrecognized
    return "Sorry, I didn't understand your request.", {}

@agent_bp.route('/agent', methods=['POST'])
def agent():
    user_text = request.json.get('text', '')
    reply, data = run_agent_logic(user_text)
    #print("reply: " + " data:" + data)
    return jsonify({ 'reply': reply, 'data': data })


