# part2/task4.py
import sys
import os
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

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

def draw_analysis_charts(gate_util_data, gate_delay_data, risk_count, total_conn):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    gate_ids = list(gate_util_data.keys())
    util_rates = [round(v * 100, 1) for v in gate_util_data.values()]
    delay_mins = [gate_delay_data[g] for g in gate_ids]

    ax1.bar(gate_ids, util_rates, color="#4682B4")
    ax1.set_title("各登机口利用率(%)")
    ax1.set_xlabel("登机口ID")
    ax1.set_ylabel("利用率 %")
    ax1.tick_params(axis="x", rotation=45)
    for idx, val in enumerate(util_rates):
        ax1.text(idx, val + 1, f"{val}%", ha="center")

    ax2.bar(gate_ids, delay_mins, color="#CD5C5C")
    ax2.set_title("各登机口累积总延误(分钟)")
    ax2.set_xlabel("登机口ID")
    ax2.set_ylabel("延误时长 min")
    ax2.tick_params(axis="x", rotation=45)
    for idx, val in enumerate(delay_mins):
        ax2.text(idx, val + 2, str(val), ha="center")

    if total_conn > 0:
        safe = total_conn - risk_count
        pie_data = [risk_count, safe]
        labels = [f"高风险旅客({risk_count}人)", f"安全旅客({safe}人)"]
        ax3.pie(pie_data, labels=labels, autopct="%1.1f%%", colors=["#FF7F50", "#90EE90"])
        ax3.set_title("中转旅客误机风险占比")
    else:
        ax3.text(0.5, 0.5, "无中转旅客数据", ha="center", va="center", fontsize=14)
        ax3.set_title("中转旅客误机风险占比")

    plt.tight_layout()
    plt.show()

def test_part2task4():
    """Task4 测试函数"""
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
    risk_list, total_conn_pax = judge_risk_passengers(gate_graph, flights, passengers, total_sim_time)
    risk_total = len(risk_list)
    affected_flight_list, avg_spread_delay, gate_delay_info = calculate_delay_spread(flights, gates)

    print("========== Test Part2 Task4 输出 ==========")
    print(f"仿真总耗时：{total_sim_time} 时间单位")
    print(f"错过中转总人数：{total_miss}")
    print(f"中转旅客总数：{total_conn_pax}，高风险旅客：{risk_total}")
    print(f"受连锁延误航班数量：{len(affected_flight_list)}，平均扩散延误：{avg_spread_delay:.2f} min")
    print("\n正在生成三张性能分析图表……")
    draw_analysis_charts(gate_util, gate_delay_info, risk_total, total_conn_pax)
    return total_sim_time, gate_util, gate_delay_info, risk_total

if __name__ == "__main__":
    test_part2task4()