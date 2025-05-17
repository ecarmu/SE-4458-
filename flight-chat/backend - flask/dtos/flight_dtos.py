class AddFlightDTO:
    def __init__(self, from_airport, to_airport, date, duration, capacity):
        self.from_airport = from_airport
        self.to_airport = to_airport
        self.date = date
        self.duration = duration
        self.capacity = capacity
