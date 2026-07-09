# part2/task3.py
import sys
import os
# 路径配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)
from part2.task1 import calc_gate_utilization, simulate_boarding
from toolbox.data_gen import load_gates, load_flights, load_passengers, init_gate_graph, link_full_system
def calculate_delay_spread(flights, gates):
    """Task3核心：计算延误连锁扩散"""
    gate_delay_record = {}
    affected_flights = []
    total_spread_delay = 0

    # 初始化每个登机口初始占用延迟时间
    for gid in gates.keys():
        gate_delay_record[gid] = 0

    for flight in flights.values():
        gate_id = flight._gate_id
        base_delay = flight.delay_minutes
        # 当前登机口已有累积延误
        gate_total_delay = gate_delay_record[gate_id]
        # 航班实际总延误 = 自身延误 + 前序航班累积延误
        real_delay = base_delay + gate_total_delay

        if real_delay > base_delay:
            # 受到连锁延误影响
            affected_flights.append({
                "flight_id": flight.flight_id,
                "gate_id": gate_id,
                "original_delay": base_delay,
                "spread_delay": gate_total_delay,
                "total_real_delay": real_delay
            })
            total_spread_delay += gate_total_delay

        # 更新登机口累积延误，传递给下一班航班
        gate_delay_record[gate_id] = real_delay

    # 计算平均连锁延误时长
    avg_spread = total_spread_delay / len(affected_flights) if affected_flights else 0
    return affected_flights, avg_spread, gate_delay_record

if __name__ == "__main__":
    # 加载数据并绑定系统
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    gate_graph = init_gate_graph()
    link_full_system(gates, flights, passengers)

    # 执行基础登机仿真
    total_sim_time, total_miss, gate_util = simulate_boarding(gates, flights, passengers)

    # Task3 延误连锁扩散计算
    affected_list, avg_spread_delay, gate_delay_info = calculate_delay_spread(flights, gates)

    # 输出报告
    print("========== Part2 Task3 航班延误连锁扩散分析报告 ==========")
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