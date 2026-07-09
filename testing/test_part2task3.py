# part2/task3.py
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

def calculate_delay_spread(flights, gates):
    gate_delay_record = {}
    affected_flights = []
    total_spread_delay = 0
    for gid in gates.keys():
        gate_delay_record[gid] = 0
    for flight in flights.values():
        gate_id = flight._gate_id
        base_delay = flight.delay_minutes
        gate_total_delay = gate_delay_record[gate_id]
        real_delay = base_delay + gate_total_delay
        if real_delay > base_delay:
            affected_flights.append({
                "flight_id": flight.flight_id,
                "gate_id": gate_id,
                "original_delay": base_delay,
                "spread_delay": gate_total_delay,
                "total_real_delay": real_delay
            })
            total_spread_delay += gate_total_delay
        gate_delay_record[gate_id] = real_delay
    avg_spread = total_spread_delay / len(affected_flights) if affected_flights else 0
    return affected_flights, avg_spread, gate_delay_record

def test_part2task3():
    """Task3 测试函数"""
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
    affected_list, avg_spread_delay, gate_delay_info = calculate_delay_spread(flights, gates)

    print("========== Test Part2 Task3 输出 ==========")
    print(f"整体登机仿真总时长：{total_sim_time} 时间单位")
    print(f"受连锁延误影响航班总数：{len(affected_list)}")
    print(f"所有受影响航班平均扩散延误时长：{avg_spread_delay:.2f} 分钟")

    print("\n===== 各登机口累积总延误 =====")
    for gid, delay in gate_delay_info.items():
        print(f"{gid} 累积延误：{delay} 分钟")

    if affected_list:
        print("\n===== 受连锁延误航班明细 =====")
        for item in affected_list:
            print(f"航班 {item['flight_id']} (登机口{item['gate_id']})")
            print(f"  自身基础延误：{item['original_delay']} min")
            print(f"  前序航班带来扩散延误：{item['spread_delay']} min")
            print(f"  实际总延误：{item['total_real_delay']} min\n")
    else:
        print("\n无航班受到连锁延误扩散影响")
    return affected_list, avg_spread_delay, gate_delay_info

if __name__ == "__main__":
    test_part2task3()