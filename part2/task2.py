# part2/task2.py
import sys
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
from part2.task1 import calc_gate_utilization, simulate_boarding
from toolbox.data_gen import load_gates, load_flights, load_passengers, init_gate_graph, link_full_system

def judge_risk_passengers(graph, flights, passengers, total_sim_time):
    """Task2核心：判定中转旅客误机高风险"""
    high_risk_list = []
    total_connect_pax = 0

    for pax in passengers:
        # 无中转航班直接跳过
        if not pax.connecting_flight_id:
            continue
        total_connect_pax += 1
        pre_flight = pax.flight
        conn_fid = pax.connecting_flight_id
        if conn_fid not in flights:
            high_risk_list.append(pax)
            continue
        conn_flight = flights[conn_fid]
        # 前序航班、中转航班必须绑定登机口
        if not pre_flight.gate or not conn_flight.gate:
            high_risk_list.append(pax)
            continue
        # 调用图模块获取两登机口最短步行时长
        path, walk_min = graph.shortest_path_between_flights(pre_flight, conn_flight)
        if walk_min is None:
            high_risk_list.append(pax)
            continue
        # 计算中转剩余时间：计划起飞时间 - 当前仿真总时间
        conn_hour = int(conn_flight.scheduled_time.split(":")[0])
        conn_total_min = conn_hour * 60
        remain_time = conn_total_min - total_sim_time
        # 剩余时间 < 步行耗时 → 高风险
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

if __name__ == "__main__":

    # 加载数据集、构建登机口拓扑图、绑定系统
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    gate_graph = init_gate_graph()
    link_full_system(gates, flights, passengers)

    # 先执行Task1登机仿真
    total_sim_time, total_miss, gate_util = simulate_boarding(gates, flights, passengers)

    # Task2：判定中转高风险旅客
    risk_pax_info, total_conn = judge_risk_passengers(gate_graph, flights, passengers, total_sim_time)

    # 输出报告
    print("========== Part2 Task2 中转旅客误机风险分析报告 ==========")
    print(f"全局登机仿真总时长：{total_sim_time} 时间单位")
    print(f"全部中转旅客总数量：{total_conn}")
    print(f"高误机风险旅客数量：{len(risk_pax_info)}")
    if total_conn > 0:
        risk_rate = len(risk_pax_info) / total_conn * 100
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