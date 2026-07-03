# 路径注入，防止单独运行模块找不到toolbox
import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.append(root)

import csv
import random
from faker import Faker
from typing import Dict, List

# 统一新包名 toolbox
from toolbox.models import Flight, Gate, Passenger, FlightStatus
from toolbox.queue import LinkedListQueue, PriorityQueue
from toolbox.graph import DirectedWeightedGraph

fake = Faker(locale="en_US")
ROOT_PATH = os.path.abspath("./")
FLIGHT_CSV = os.path.join(ROOT_PATH, "flights_dataset.csv")
GATE_CSV = os.path.join(ROOT_PATH, "gates_dataset.csv")
PASSENGER_CSV = os.path.join(ROOT_PATH, "passengers_dataset.csv")

def generate_gates_csv(gate_num: int = 12):
    terminals = ["T1", "T2"]
    with open(GATE_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["gate_id", "terminal", "capacity", "is_international"])
        for i in range(1, gate_num+1):
            gid = f"G{i:02d}"
            ter = random.choice(terminals)
            intl = ter == "T2"
            cap = random.randint(80,220)
            w.writerow([gid, ter, cap, intl])

def generate_flights_csv(flight_num: int = 40):
    airlines = ["Air China", "China Eastern", "China Southern", "Hainan Airlines"]
    cities = ["Beijing","Shanghai","Guangzhou","Chengdu","Shenzhen"]
    status_list = [s.value for s in FlightStatus]
    gate_ids = [f"G{i:02d}" for i in range(1,13)]
    with open(FLIGHT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["flight_id","airline","origin_or_destination","scheduled_time","status","gate_id","passenger_count","delay_minutes"])
        for _ in range(flight_num):
            fid = f"CA{random.randint(1000,9999)}"
            air = random.choice(airlines)
            city = random.choice(cities)
            time = fake.time("%H:%M")
            stat = random.choice(status_list)
            gate = random.choice(gate_ids)
            pcount = random.randint(50,320)
            delay = random.randint(10,120) if stat == FlightStatus.DELAYED.value else 0
            w.writerow([fid, air, city, time, stat, gate, pcount, delay])

def generate_passengers_csv(pass_num: int = 200):
    flight_ids = []
    if os.path.exists(FLIGHT_CSV):
        with open(FLIGHT_CSV, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                flight_ids.append(row["flight_id"])
    with open(PASSENGER_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["passenger_id","name","boarding_group","has_special_needs","connecting_flight_id"])
        for idx in range(1, pass_num+1):
            pid = f"P{idx:04d}"
            name = f"{fake.first_name()} {fake.last_name()}"
            group = random.randint(1,5)
            special = random.choices([True,False], weights=[0.08,0.92])[0]
            conn = random.choice(flight_ids) if flight_ids and random.random() <0.25 else None
            w.writerow([pid, name, group, special, conn])

def generate_all_datasets():
    generate_gates_csv(12)
    generate_flights_csv(40)
    generate_passengers_csv(200)
    print(f"CSV生成完成，路径：{ROOT_PATH}")
    print("flights_dataset.csv\ngates_dataset.csv\npassengers_dataset.csv")

def load_gates() -> Dict[str, Gate]:
    gate_dict = {}
    with open(GATE_CSV, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
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
        r = csv.DictReader(f)
        for row in r:
            fobj = Flight(
                flight_id=row["flight_id"],
                airline=row["airline"],
                origin_or_destination=row["origin_or_destination"],
                scheduled_time=row["scheduled_time"],
                status=FlightStatus(row["status"]),
                gate_id=row["gate_id"],
                passenger_count=int(row["passenger_count"]),
                delay_minutes=int(row["delay_minutes"])
            )
            flight_dict[fobj.flight_id] = fobj
    return flight_dict

def load_passengers() -> List[Passenger]:
    plist = []
    with open(PASSENGER_CSV, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            p = Passenger(
                passenger_id=row["passenger_id"],
                name=row["name"],
                boarding_group=int(row["boarding_group"]),
                has_special_needs=eval(row["has_special_needs"]),
                connecting_flight_id=row["connecting_flight_id"] if row["connecting_flight_id"] else None
            )
            plist.append(p)
    return plist

def init_gate_graph() -> DirectedWeightedGraph:
    graph = DirectedWeightedGraph()
    gates = load_gates()
    for g in gates.values():
        graph.add_gate(g)
    gate_ids = list(gates.keys())
    for start in gate_ids:
        cnt = random.randint(1,4)
        targets = random.sample([g for g in gate_ids if g != start], k=cnt)
        for end in targets:
            t = random.randint(3,12)
            graph.add_path(start, end, t)
    return graph