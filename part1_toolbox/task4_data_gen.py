import csv
import random
import os
from faker import Faker
from typing import Dict, List
from part1_toolbox.task1_models import Flight, Gate, Passenger, FlightStatus
from part1_toolbox.task2_queue import LinkedListQueue, PriorityQueue
from part1_toolbox.task3_graph import DirectedWeightedGraph

fake = Faker(locale="en_US")
# 项目根目录路径
ROOT_PATH = os.path.abspath("./")
FLIGHT_CSV = os.path.join(ROOT_PATH, "flights_dataset.csv")
GATE_CSV = os.path.join(ROOT_PATH, "gates_dataset.csv")
PASSENGER_CSV = os.path.join(ROOT_PATH, "passengers_dataset.csv")

# ---------------------- CSV生成函数 ----------------------
def generate_gates_csv(gate_num: int = 12):
    """生成登机口CSV，真实机场：T1国内，T2国际，容量80~220"""
    terminals = ["T1", "T2"]
    with open(GATE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["gate_id", "terminal", "capacity", "is_international"])
        for i in range(1, gate_num+1):
            gid = f"G{i:02d}"
            ter = random.choice(terminals)
            is_intl = ter == "T2"
            cap = random.randint(80, 220)
            writer.writerow([gid, ter, cap, is_intl])

def generate_flights_csv(flight_num: int = 40):
    """生成航班CSV，真实航线人数50~320，延误0~120分钟"""
    airlines = ["Air China", "China Eastern", "China Southern", "Hainan Airlines"]
    cities = ["Beijing", "Shanghai", "Guangzhou", "Chengdu", "Shenzhen"]
    status_list = [s.value for s in FlightStatus]
    gate_ids = [f"G{i:02d}" for i in range(1, 13)]
    with open(FLIGHT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["flight_id", "airline", "origin_or_destination", "scheduled_time",
                         "status", "gate_id", "passenger_count", "delay_minutes"])
        for _ in range(flight_num):
            fid = f"CA{random.randint(1000, 9999)}"
            airline = random.choice(airlines)
            city = random.choice(cities)
            time = fake.time("%H:%M")
            status = random.choice(status_list)
            gid = random.choice(gate_ids)
            p_count = random.randint(50, 320)
            delay = random.randint(10, 120) if status == FlightStatus.DELAYED.value else 0
            writer.writerow([fid, airline, city, time, status, gid, p_count, delay])

def generate_passengers_csv(pass_num: int = 200):
    """乘客英文名使用美式真实姓名，转机ID随机关联航班"""
    # 预读取航班ID用于转机匹配
    flight_ids = []
    if os.path.exists(FLIGHT_CSV):
        with open(FLIGHT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                flight_ids.append(row["flight_id"])
    with open(PASSENGER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["passenger_id", "name", "boarding_group", "has_special_needs", "connecting_flight_id"])
        for idx in range(1, pass_num+1):
            pid = f"P{idx:04d}"
            full_name = f"{fake.first_name()} {fake.last_name()}"
            group = random.randint(1,5)
            special = random.choices([True, False], weights=[0.08, 0.92])[0]
            conn_id = random.choice(flight_ids) if flight_ids and random.random() < 0.25 else None
            writer.writerow([pid, full_name, group, special, conn_id])

# 一键生成全部CSV
def generate_all_datasets():
    generate_gates_csv(gate_num=12)
    generate_flights_csv(flight_num=40)
    generate_passengers_csv(pass_num=200)
    print(f"CSV文件已生成至项目根目录：{ROOT_PATH}")
    print("- flights_dataset.csv")
    print("- gates_dataset.csv")
    print("- passengers_dataset.csv")

# ---------------------- CSV加载函数 ----------------------
def load_gates() -> Dict[str, Gate]:
    gate_dict = {}
    with open(GATE_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            g = Gate(
                gate_id=row["gate_id"],
                terminal=row["terminal"],
                capacity=int(row["capacity"]),
                is_international=eval(row["is_international"])
            )
            g.regular_queue = LinkedListQueue()
            g.priority_queue = PriorityQueue()
            gate_dict[g.gate_id] = g
    return gate_dict

def load_flights() -> Dict[str, Flight]:
    flight_dict = {}
    with open(FLIGHT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            f = Flight(
                flight_id=row["flight_id"],
                airline=row["airline"],
                origin_or_destination=row["origin_or_destination"],
                scheduled_time=row["scheduled_time"],
                status=FlightStatus(row["status"]),
                gate_id=row["gate_id"],
                passenger_count=int(row["passenger_count"]),
                delay_minutes=int(row["delay_minutes"])
            )
            flight_dict[f.flight_id] = f
    return flight_dict

def load_passengers() -> List[Passenger]:
    passenger_list = []
    with open(PASSENGER_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = Passenger(
                passenger_id=row["passenger_id"],
                name=row["name"],
                boarding_group=int(row["boarding_group"]),
                has_special_needs=eval(row["has_special_needs"]),
                connecting_flight_id=row["connecting_flight_id"] if row["connecting_flight_id"] else None
            )
            passenger_list.append(p)
    return passenger_list

# 初始化登机口网络图
def init_gate_graph() -> DirectedWeightedGraph:
    graph = DirectedWeightedGraph()
    gates = load_gates()
    # 加载所有登机口节点
    for g in gates.values():
        graph.add_gate(g)
    # 随机生成步行路径
    gate_id_list = list(gates.keys())
    for g1 in gate_id_list:
        connect_num = random.randint(1,4)
        targets = random.sample([g for g in gate_id_list if g != g1], k=connect_num)
        for g2 in targets:
            walk_t = random.randint(3,12)
            graph.add_path(g1, g2, walk_t)
    return graph