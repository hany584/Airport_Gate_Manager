# 全局路径注入，解决单独运行模块找不到toolbox包
import sys
import os
# 获取项目顶层根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 系统标准库
import csv
import random
from faker import Faker
from typing import Dict, List

# 全局标准绝对导入
from toolbox.models import Flight, Gate, Passenger, FlightStatus
from toolbox.queue import LinkedListQueue  # 改进：只导入同步FIFO，不再单独导入独立PriorityQueue
from toolbox.graph import DirectedWeightedGraph

# 英文虚拟数据生成器
fake = Faker(locale="en_US")
# CSV输出路径：项目顶层文件夹
ROOT_PATH = os.path.abspath("./")
FLIGHT_CSV = os.path.join(ROOT_PATH, "flights_dataset.csv")
GATE_CSV = os.path.join(ROOT_PATH, "gates_dataset.csv")
PASSENGER_CSV = os.path.join(ROOT_PATH, "passengers_dataset.csv")

# -------------------------- CSV生成函数 --------------------------
def generate_gates_csv(gate_num: int = 12):
    """生成廊桥CSV，T1国内/T2国际，容量80~220"""
    terminals = ["T1", "T2"]
    with open(GATE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["gate_id", "terminal", "capacity", "is_international"])
        for i in range(1, gate_num + 1):
            gate_id = f"G{i:02d}"
            ter = random.choice(terminals)
            is_intl = ter == "T2"
            cap = random.randint(80, 220)
            writer.writerow([gate_id, ter, cap, is_intl])

def generate_flights_csv(flight_num: int = 40):
    """生成航班CSV，载客50~320，仅延误航班分配延误时长"""
    airlines = ["Air China", "China Eastern", "China Southern", "Hainan Airlines"]
    cities = ["Beijing", "Shanghai", "Guangzhou", "Chengdu", "Shenzhen"]
    status_list = [s.value for s in FlightStatus]
    gate_id_list = [f"G{i:02d}" for i in range(1, 13)]
    with open(FLIGHT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["flight_id", "airline", "origin_or_destination", "scheduled_time",
                         "status", "gate_id", "passenger_count", "delay_minutes"])
        for _ in range(flight_num):
            flight_id = f"CA{random.randint(1000, 9999)}"
            air = random.choice(airlines)
            city = random.choice(cities)
            time = fake.time("%H:%M")
            status = random.choice(status_list)
            gate = random.choice(gate_id_list)
            passenger_count = random.randint(50, 320)
            delay = random.randint(10, 120) if status == FlightStatus.DELAYED.value else 0
            writer.writerow([flight_id, air, city, time, status, gate, passenger_count, delay])

def generate_passengers_csv(pass_num: int = 200):
    """生成旅客CSV，8%特殊旅客，25%转机旅客，纯英文姓名"""
    flight_id_list = []
    if os.path.exists(FLIGHT_CSV):
        with open(FLIGHT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                flight_id_list.append(row["flight_id"])
    with open(PASSENGER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["passenger_id", "name", "boarding_group", "has_special_needs", "connecting_flight_id"])
        for idx in range(1, pass_num + 1):
            p_id = f"P{idx:04d}"
            full_name = f"{fake.first_name()} {fake.last_name()}"
            group = random.randint(1, 5)
            special = random.choices([True, False], weights=[0.08, 0.92])[0]
            conn_flight = random.choice(flight_id_list) if flight_id_list and random.random() < 0.25 else None
            writer.writerow([p_id, full_name, group, special, conn_flight])

# 一键生成全部三份CSV数据集
def generate_all_datasets():
    generate_gates_csv(gate_num=12)
    generate_flights_csv(flight_num=40)
    generate_passengers_csv(pass_num=200)
    print(f"CSV文件生成完成，存放路径：{ROOT_PATH}")
    print("1. flights_dataset.csv")
    print("2. gates_dataset.csv")
    print("3. passengers_dataset.csv")

# 加载廊桥CSV，实例化Gate并绑定**同步一体化FIFO队列**（改进1）
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
            # 改进1：移除独立双队列regular_queue / priority_queue，统一使用内置同步堆的LinkedListQueue
            g.boarding_queue = LinkedListQueue()
            gate_dict[g.gate_id] = g
    return gate_dict

# 加载航班CSV，实例化Flight对象
def load_flights() -> Dict[str, Flight]:
    flight_dict = {}
    with open(FLIGHT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            flight_obj = Flight(
                flight_id=row["flight_id"],
                airline=row["airline"],
                origin_or_destination=row["origin_or_destination"],
                scheduled_time=row["scheduled_time"],
                status=FlightStatus(row["status"]),
                gate_id=row["gate_id"],
                passenger_count=int(row["passenger_count"]),
                delay_minutes=int(row["delay_minutes"])
            )
            flight_dict[flight_obj.flight_id] = flight_obj
    return flight_dict

# 加载旅客CSV，生成Passenger列表
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

# 初始化廊桥有向加权图
def init_gate_graph() -> DirectedWeightedGraph:
    graph = DirectedWeightedGraph()
    gates = load_gates()
    for gate_obj in gates.values():
        graph.add_gate(gate_obj)
    gate_id_list = list(gates.keys())
    for start_gate in gate_id_list:
        connect_count = random.randint(1, 4)
        target_gates = random.sample([g for g in gate_id_list if g != start_gate], k=connect_count)
        for end_gate in target_gates:
            walk_time = random.randint(3, 12)
            graph.add_path(start_gate, end_gate, walk_time)
    return graph

# -------------------------- 新增核心联动函数（匹配任务2：打通图、Gate、Flight、乘客一体化系统） --------------------------
def link_full_system(gate_map: Dict[str, Gate], flight_map: Dict[str, Flight], passenger_list: List[Passenger]):
    """
    改进2：完整联动整套业务系统，满足任务2要求：
    1. Flight绑定真实Gate对象（不只用gate_id）
    2. Gate绑定停靠的Flight
    3. 所有Passenger绑定对应Flight并加入登机同步队列
    """
    # 1. 航班绑定Gate完整对象
    for flight in flight_map.values():
        target_gate = gate_map.get(flight._gate_id)
        if target_gate:
            flight.bind_gate(target_gate)
            target_gate.dock_flight(flight)

    # 2. 乘客随机分配至航班，双向绑定航班并加入FIFO队列（堆自动同步）
    flight_id_list = list(flight_map.keys())
    for pax in passenger_list:
        target_flight_id = random.choice(flight_id_list)
        target_flight = flight_map[target_flight_id]
        target_flight.add_passenger(pax)

# -------------------------- 新增演示入口（匹配任务3：main使用自动生成数据集展示双队列） --------------------------
def demo_system():
    """完整系统演示，使用自动生成CSV数据集，打印FIFO与同步优先列表"""
    # 1. 生成批量数据集（替代手写3个乘客）
    generate_all_datasets()

    # 2. 加载所有模型
    gate_dict = load_gates()
    flight_dict = load_flights()
    pax_list = load_passengers()
    gate_graph = init_gate_graph()

    # 3. 联动Gate-Flight-Passenger，整合为一套系统
    link_full_system(gate_dict, flight_dict, pax_list)

    # 4. 打印登机口拓扑图
    print("\n======== 机场登机口拓扑图 ========")
    gate_graph.display_graph()

    # 5. 遍历航班，展示FIFO队列与自动同步的优先堆视图
    print("\n======== 各航班登机队列演示 ========")
    for flight in list(flight_dict.values())[:3]:  # 展示前3架航班避免输出过长
        print(f"\n--- {flight} ---")
        flight.boarding_queue.display()
        flight.boarding_queue.display_priority_view()
        # 校验FIFO与堆数据一致性
        sync_ok = flight.boarding_queue.check_coherence()
        print(f"FIFO与优先堆数据一致性校验: {'✅ 通过' if sync_ok else '❌ 不一致'}")

        # 演示出队操作，验证单向同步更新
        print("> 执行一次出队操作：")
        removed_p = flight.boarding_queue.dequeue()
        print(f"移出旅客: {removed_p}")
        flight.boarding_queue.display()
        flight.boarding_queue.display_priority_view()
        sync_after = flight.boarding_queue.check_coherence()
        print(f"出队后一致性校验: {'✅ 通过' if sync_after else '❌ 不一致'}")

# 程序主入口
if __name__ == "__main__":
    demo_system()