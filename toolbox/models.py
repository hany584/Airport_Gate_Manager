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
        # 改进1：不再仅存储gate_id字符串，存储完整Gate对象
        self.gate: Gate | None = None
        self._gate_id = gate_id  # 保留原id字段用于匹配Gate实例
        self.passenger_count = passenger_count
        self.delay_minutes = delay_minutes
        # 改进2：绑定当前航班所有乘客列表，建立乘客-航班双向关联
        self.passengers: list[Passenger] = []

    # 改进3：提供绑定Gate完整对象的方法
    def bind_gate(self, gate_obj: "Gate") -> None:
        if gate_obj.gate_id == self._gate_id:
            self.gate = gate_obj
        else:
            raise ValueError(f"Gate ID不匹配：航班{self.flight_id}预期{self._gate_id}，传入{gate_obj.gate_id}")

    # 改进4：绑定乘客到当前航班，实现乘客与航班关联
    def add_passenger(self, passenger: "Passenger") -> None:
        passenger.bind_flight(self)
        self.passengers.append(passenger)

    def __repr__(self):
        gate_info = self.gate.gate_id if self.gate else f"未绑定Gate({self._gate_id})"
        return f"<Flight {self.flight_id} | {self.airline} | Gate:{gate_info} | Status:{self.status.value}>"

class Gate:
    def __init__(self, gate_id: str, terminal: str, capacity: int, is_international: bool):
        self.gate_id = gate_id
        self.terminal = terminal
        self.capacity = capacity
        self.is_international = is_international
        # 改进5：删除分开的两个队列属性，统一使用同步FIFO队列（内置自动同步优先堆）
        self.boarding_queue = None
        # 改进6：存储停靠在本登机口的航班，打通图与航班数据
        self.docked_flight: Flight | None = None
        # 改进7：存储相邻登机口，构建登机口连通图结构
        self.adjacent_gates: list["Gate"] = []

    # 改进8：登机口之间建立连通关系（图结构）
    def connect_adjacent_gate(self, other_gate: "Gate") -> None:
        if other_gate not in self.adjacent_gates:
            self.adjacent_gates.append(other_gate)
            other_gate.connect_adjacent_gate(self)

    # 改进9：绑定停靠在该登机口的航班
    def dock_flight(self, flight_obj: Flight) -> None:
        if flight_obj._gate_id == self.gate_id:
            self.docked_flight = flight_obj
        else:
            raise ValueError(f"航班{flight_obj.flight_id}Gate ID与登机口{self.gate_id}不匹配")

    def __repr__(self):
        flight_info = self.docked_flight.flight_id if self.docked_flight else "无停靠航班"
        adj_ids = [g.gate_id for g in self.adjacent_gates]
        return f"<Gate {self.gate_id} | Terminal:{self.terminal} | DockedFlight:{flight_info} | AdjacentGates:{adj_ids}>"

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
        # 改进10：新增属性，存储乘客所属航班，实现双向关联
        self.flight: Flight | None = None

    # 改进11：绑定乘客所属航班
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