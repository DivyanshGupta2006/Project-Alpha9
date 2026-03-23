import queue

class Event:
    pass

class MarketEvent(Event):
    def __init__(self, timestamp):
        self.type = "MARKET"
        self.timestamp = timestamp

class SignalEvent(Event):
    def __init__(self, timestamp, fiducia):
        self.type = "SIGNAL"
        self.timestamp = timestamp
        self.fiducia = fiducia

class OrderEvent(Event):
    def __init__(self, timestamp, description):
        self.type = "ORDER"
        self.timestamp = timestamp
        self.description = description

class FillEvent(Event):
    def __init__(self, timestamp, description, cash_change, transaction_cost):
        self.type = "FILL"
        self.timestamp = timestamp
        self.description = description
        self.cash_change = cash_change
        self.transaction_cost = transaction_cost

class EventQueue:
    def __init__(self):
        self._events = queue.Queue()

    def get_event(self):
        try:
            return self._events.get(block=False)
        except queue.Empty:
            return None

    def put_event(self, event):
        self._events.put(event)

    def empty(self):
        return self._events.empty()

    def size(self):
        return self._events.qsize()