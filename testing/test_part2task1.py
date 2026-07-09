# part2/task1.py
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

def calc_gate_utilization(gate, total_sim_time):
    if total_sim_time == 0:
        return 0.0
    busy = gate.busy_time if hasattr(gate, "busy_time") else 0
    return round(busy / total_sim_time, 3)

def simulate_boarding(gates, flights, passengers):
    missed_conn = 0
    sim_time = 0
    max_time = 500
    for g in gates.values():
        g.busy_time = 0
    flight_pass_map = {}
    for f in flights.values():
        flight_pass_map[f.flight_id] = []
    for p in passengers:
        flight_pass_map[p.flight.flight_id].append(p)

    while sim_time < max_time:
        any_boarding = False
        for g in gates.values():
            if g.boarding_queue.size() > 0:
                g.boarding_queue.dequeue()
                g.busy_time += 1
                any_boarding = True
        if not any_boarding:
            break
        sim_time += 1

    for p in passengers:
        if p.connecting_flight_id is None:
            continue
        conn_fid = p.connecting_flight_id
        if conn_fid not in flights:
            missed_conn += 1
            continue
        conn_flight = flights[conn_fid]
        if sim_time >= int(conn_flight.scheduled_time.split(":")[0]) * 60:
            missed_conn += 1

    util_result = {}
    for gid, g in gates.items():
        util_result[gid] = calc_gate_utilization(g, sim_time)
    return sim_time, missed_conn, util_result

def test_part2task1():
    """Task1 测试函数"""
    data_gen_mod = __import__("toolbox.data_gen", fromlist=[
        "load_gates", "load_flights", "load_passengers", "link_full_system"
    ])
    load_gates = data_gen_mod.load_gates
    load_flights = data_gen_mod.load_flights
    load_passengers = data_gen_mod.load_passengers
    link_full_system = data_gen_mod.link_full_system

    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    link_full_system(gates, flights, passengers)

    total_time, miss_count, gate_util = simulate_boarding(gates, flights, passengers)

    print("========== Test Part2 Task1 输出 ==========")
    print(f"1. 全部航班完成登机总时长：{total_time} 时间单位")
    print(f"2. 错过中转衔接航班旅客总数：{miss_count}")
    print("\n3. 各登机口利用率：")
    for gate_id, rate in gate_util.items():
        print(f"{gate_id}：{rate * 100:.1f}%")
    return total_time, miss_count, gate_util

if __name__ == "__main__":
    test_part2task1()