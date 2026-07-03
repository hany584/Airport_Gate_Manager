from enum import Enum

class FlightStatus(Enum):
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    BOARDING = "BOARDING"
    DEPARTED = "DEPARTED"
    CANCELLED = "CANCELLED"

class Flight:
    def __init__(self, flight_id: str, airline: str, origin_or_destination: str,
                 scheduled_time: str, status: FlightStatus, gate_id: str,
                 passenger_count: int, delay_minutes: int = 0):
        self.flight_id = flight_id
        self.airline = airline
        self.origin_or_destination = origin_or_destination
        self.scheduled_time = scheduled_time
        self.status = status
        self.gate_id = gate_id
        self.passenger_count = passenger_count
        self.delay_minutes = delay_minutes

    def __repr__(self):
        return f"<Flight {self.flight_id} | {self.airline} | Status:{self.status.value}>"

class Gate:
    def __init__(self, gate_id: str, terminal: str, capacity: int, is_international: bool):
        self.gate_id = gate_id
        self.terminal = terminal
        self.capacity = capacity
        self.is_international = is_international
        self.regular_queue = None    # 绑定FIFO普通队列
        self.priority_queue = None   # 绑定优先登机队列

    def __repr__(self):
        return f"<Gate {self.gate_id} | Terminal:{self.terminal}>"

class Passenger:
    def __init__(self, passenger_id: str, name: str, boarding_group: int,
                 has_special_needs: bool, connecting_flight_id: str = None):
        if not 1 <= boarding_group <= 5:
            raise ValueError("boarding_group必须为1~5整数")
        self.passenger_id = passenger_id
        self.name = name
        self.boarding_group = boarding_group
        self.has_special_needs = has_special_needs
        self.connecting_flight_id = connecting_flight_id

    def __repr__(self):
        return f"<Passenger {self.passenger_id} | Name:{self.name}>"

    def get_priority_score(self) -> int:
        """优先级打分：分数越高优先登机
        基础10分
        特殊旅客+50，1组旅客+40，转机旅客+30
        """
        base = 10
        if self.has_special_needs:
            base += 50
        if self.boarding_group == 1:
            base += 40
        if self.connecting_flight_id is not None:
            base += 30
        return base