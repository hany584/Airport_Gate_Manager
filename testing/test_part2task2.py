# part2/task2.py
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

def judge_risk_passengers(graph, flights, passengers, total_sim_time):
    high_risk_list = []
    total_connect_pax = 0
    for pax in passengers:
        if not pax.connecting_flight_id:
            continue
        total_connect_pax += 1
        pre_flight = pax.flight
        conn_fid = pax.connecting_flight_id
        if conn_fid not in flights:
            high_risk_list.append(pax)
            continue
        conn_flight = flights[conn_fid]
        if not pre_flight.gate or not conn_flight.gate:
            high_risk_list.append(pax)
            continue
        path, walk_min = graph.shortest_path_between_flights(pre_flight, conn_flight)
        if walk_min is None:
            high_risk_list.append(pax)
            continue
        conn_hour = int(conn_flight.scheduled_time.split(":")[0])
        conn_total_min = conn_hour * 60
        remain_time = conn_total_min - total_sim_time
        if remain_time < walk_min:
            high_risk_list.append({
                "passenger": pax,
                "walk_time": walk_min,
                "remain_time": remain_time,
                "pre_gate": pre_flight.gate.gate_id,
                "conn_gate": conn_flight.gate.gate_id,
                "shortest_path": path
            })
    return high_risk_list, total_connect_pax

def test_part2task2():
    """Task2 测试函数"""
    data_gen_mod = __import__("toolbox.data_gen", fromlist=[
        "load_gates", "load_flights", "load_passengers",
        "init_gate_graph", "link_full_system"
    ])
    load_gates = data_gen_mod.load_gates
    load_flights = data_gen_mod.load_flights
    load_passengers = data_gen_mod.load_passengers
    init_gate_graph = data_gen_mod.init_gate_graph
    link_full_system = data_gen_mod.link_full_system

    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    gate_graph = init_gate_graph()
    link_full_system(gates, flights, passengers)

    total_sim_time, total_miss, gate_util = simulate_boarding(gates, flights, passengers)
    risk_pax_info, total_conn = judge_risk_passengers(gate_graph, flights, passengers, total_sim_time)
    risk_count = len(risk_pax_info)

    print("========== Test Part2 Task2 输出 ==========")
    print(f"全局登机仿真总时长：{total_sim_time} 时间单位")
    print(f"全部中转旅客总数量：{total_conn}")
    print(f"高误机风险旅客数量：{risk_count}")
    if total_conn > 0:
        risk_rate = risk_count / total_conn * 100
        print(f"中转旅客风险占比：{risk_rate:.2f}%")

    print("\n===== 高风险旅客明细 =====")
    for item in risk_pax_info:
        if isinstance(item, dict):
            p = item["passenger"]
            print(f"旅客ID:{p.passenger_id} 姓名:{p.name}")
            print(f"  前序登机口:{item['pre_gate']} → 中转登机口:{item['conn_gate']}")
            print(f"  最短步行路径:{item['shortest_path']} 步行耗时:{item['walk_time']}分钟")
            print(f"  剩余可用中转时间:{item['remain_time']}分钟（时间不足，高风险）\n")
        else:
            print(f"旅客{item.passenger_id}：中转航班不存在/无登机口绑定，极高误机风险\n")
    return risk_pax_info, total_conn

if __name__ == "__main__":
    test_part2task2()