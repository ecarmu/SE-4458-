
# Airline Ticketing System API – SE4458 Midterm Project

This project is an implementation of a RESTful API for an airline ticketing system, designed as part of the SE4458 Software Architecture and Design midterm.



## Deliverables
source code:  https://github.com/ecarmu/SE-4458-/tree/main/midterm

deployed at:  https://ardaharman.pythonanywhere.com/apidocs/

presentation: https://youtu.be/IAdVpyamdwg


## ER Diagram
![ER Diagram](https://github.com/ecarmu/SE-4458-/blob/main/midterm/ER_diagram.png)
    

## Assumptions Made

1. In `query_flights`, I used **`min_seats`** instead of `"number of people"` as a query parameter.
2. At `buy_tickets`, I didn't decrease the capacity on purpose but increase the `booked` count each time
3. In `Buy Ticket`, `Check-in`, and `Query Flight Passenger List`, I used **`flight_id`** instead of `"Flight Number + Date"` for simplicity and accuracy.
4. No `user` will have the same `name` and `surname`





## Authentication
   `username: admin`
   `password: password`


## Features Implemented

- **Add Flight** (authentication required)
- **Query Flights** (with paging, no auth)
- **Buy Ticket** (authentication required, capacity control)
- **Check-in** (no auth, assigns seat)
- **Query Flight Passenger List** (authentication required, paging)

## Tech Stack

- Python (Flask)
- SQLite (via SQLAlchemy)
- Swagger (Flasgger) for API documentation
- JWT for authentication

## Usage Notes

- All date inputs must be in the format `YYYY-MM-DD`
- Swagger UI validates required fields like `date_from` and `date_to`
- Paging is applied to query endpoints (default page size = 10)

