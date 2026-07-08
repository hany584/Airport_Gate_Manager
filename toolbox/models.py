from enum import Enum
from typing import Optional
# 此处导入之前改造完成的链表队列类（LinkedListQueue、ListNode、PriorityQueue）
from toolbox.queue import ListNode, LinkedListQueue, PriorityQueue

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
        self.gate: Optional["Gate"] = None
        self._gate_id = gate_id
        self.passenger_count = passenger_count
        self.delay_minutes = delay_minutes
        self.passengers: list["Passenger"] = []

    def bind_gate(self, gate_obj: "Gate") -> None:
        if gate_obj.gate_id == self._gate_id:
            self.gate = gate_obj
            # NEW 改动：绑定Gate时，航班所有乘客自动加入登机口登机队列
            for pax in self.passengers:
                gate_obj.boarding_queue.enqueue(pax)
        else:
            raise ValueError(f"Gate ID不匹配：航班{self.flight_id}预期{self._gate_id}，传入{gate_obj.gate_id}")

    def add_passenger(self, passenger: "Passenger") -> None:
        passenger.bind_flight(self)
        self.passengers.append(passenger)
        # NEW 改动：新增乘客时，如果航班已绑定登机口，直接加入Gate的同步队列
        if self.gate is not None and self.gate.boarding_queue is not None:
            self.gate.boarding_queue.enqueue(passenger)

    def __repr__(self):
        gate_info = self.gate.gate_id if self.gate else f"未绑定Gate({self._gate_id})"
        return f"<Flight {self.flight_id} | {self.airline} | Gate:{gate_info} | Status:{self.status.value}>"

class Gate:
    def __init__(self, gate_id: str, terminal: str, capacity: int, is_international: bool):
        self.gate_id = gate_id
        self.terminal = terminal
        self.capacity = capacity
        self.is_international = is_international
        # MODIFIED 改动：初始化同步FIFO队列（内置自动维护的优先堆）
        self.boarding_queue: Optional[LinkedListQueue] = LinkedListQueue()
        self.docked_flight: Optional[Flight] = None
        self.adjacent_gates: list["Gate"] = []

    def connect_adjacent_gate(self, other_gate: "Gate") -> None:
        if other_gate not in self.adjacent_gates:
            self.adjacent_gates.append(other_gate)
            other_gate.connect_adjacent_gate(self)

    def dock_flight(self, flight_obj: Flight) -> None:
        if flight_obj._gate_id == self.gate_id:
            self.docked_flight = flight_obj
            flight_obj.bind_gate(self) # NEW 改动：双向绑定Flight与Gate
        else:
            raise ValueError(f"航班{flight_obj.flight_id}Gate ID与登机口{self.gate_id}不匹配")

    # NEW 新增辅助方法：一键打印当前登机口FIFO与优先队列
    def show_all_queues(self) -> None:
        print(f"\n==== Gate {self.gate_id} 登机队列 ====")
        self.boarding_queue.display_all()

    def __repr__(self):
        flight_info = self.docked_flight.flight_id if self.docked_flight else "无停靠航班"
        adj_ids = [g.gate_id for g in self.adjacent_gates]
        queue_size = self.boarding_queue.size() if self.boarding_queue else 0
        return f"<Gate {self.gate_id} | Terminal:{self.terminal} | DockedFlight:{flight_info} | QueueSize:{queue_size} | AdjacentGates:{adj_ids}>"

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
        self.flight: Optional[Flight] = None

    def bind_flight(self, flight_obj: Flight) -> None:
        self.flight = flight_obj

    def __repr__(self):
        flight_id = self.flight.flight_id if self.flight else "未分配航班"
        return f"<Passenger {self.passenger_id} | Name:{self.name} | Flight:{flight_id}>"

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