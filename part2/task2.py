# part2/task2.py
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

from toolbox.data_gen import load_gates, load_flights, load_passengers, init_gate_graph

MIN_CONNECT_BUFFER = 15

if __name__ == "__main__":
    # 加载数据
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    graph = init_gate_graph()

    # 过滤登机口不存在的航班，防止KeyError
    valid_gates = set(gates.keys())
    flights = {fid: f for fid, f in flights.items() if f.gate_id in valid_gates}

    flight_gate_map = {f.flight_id: f.gate_id for f in flights.values()}
    risk_passenger_list = []

    # 遍历旅客，只判断connecting_flight_id
    for pax in passengers:
        conn_flight_id = pax.connecting_flight_id
        # 没有接续航班直接跳过
        if not conn_flight_id or conn_flight_id not in flight_gate_map:
            continue

        depart_gate = flight_gate_map[conn_flight_id]
        all_gate_list = list(flight_gate_map.values())
        arrival_gate = all_gate_list[0]
        _, walk_minute = graph.find_shortest_path(arrival_gate, depart_gate)

        flight_info = flights[conn_flight_id]
        available_time = 60 - flight_info.delay_minutes

        if available_time < walk_minute + MIN_CONNECT_BUFFER:
            risk_passenger_list.append((pax.name, walk_minute, available_time))

    # 输出结果
    print("===== Task2 高风险转机旅客 =====")
    if len(risk_passenger_list) == 0:
        print("暂无存在误机风险的转机旅客")
    else:
        for name, walk_time, free_time in risk_passenger_list[:5]:
            print(f"旅客{name}，步行耗时{walk_time}分钟，剩余转机时间{free_time}分钟，存在误机风险")