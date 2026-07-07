# part2/task1.py
import sys
import os
# 拿到项目根目录路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 把根目录加入系统路径，解决toolbox导入
sys.path.append(BASE_DIR)
# 切换工作目录到项目根目录，csv就能正常读取
os.chdir(BASE_DIR)

from collections import defaultdict
from toolbox.data_gen import load_gates, load_flights, load_passengers, init_gate_graph

class BoardingSimulator:
    def __init__(self, gates, flights, passengers):
        self.gates = gates
        self.flights = flights
        self.passengers = passengers
        self.stats = {
            "sim_total_min": 0,
            "gate_busy_min": defaultdict(int)
        }

    def allocate_passengers(self):
        flight_pax = defaultdict(list)
        for p in self.passengers:
            fid = p.connecting_flight_id
            if fid:
                flight_pax[fid].append(p)
        for fid, pax_list in flight_pax.items():
            if fid not in self.flights:
                continue
            gate_id = self.flights[fid].gate_id
            for p in pax_list:
                self.gates[gate_id].priority_queue.enqueue(p)

    def time_step(self):
        for gid, gate in self.gates.items():
            if gate.priority_queue.size() > 0:
                gate.priority_queue.dequeue()
                self.stats["gate_busy_min"][gid] += 1

    def run(self, max_time=300):
        self.allocate_passengers()
        clock = 0
        while clock < max_time:
            has_person = any(g.priority_queue.size()>0 for g in self.gates.values())
            if not has_person:
                break
            self.time_step()
            clock += 1
        self.stats["sim_total_min"] = clock
        return self.stats

if __name__ == "__main__":
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()

    # 过滤登机口不存在的航班，解决KeyError:G12
    valid_gates = set(gates.keys())
    flights = {fid: f for fid, f in flights.items() if f.gate_id in valid_gates}

    sim = BoardingSimulator(gates, flights, passengers)
    res = sim.run()

    print("===== Task1 登机仿真结果 =====")
    print(f"总耗时：{res['sim_total_min']} 分钟")
    for gid, busy in res["gate_busy_min"].items():
        ratio = round(busy / res["sim_total_min"], 3)
        print(f"{gid} 利用率：{ratio}")
        