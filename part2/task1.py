# part2/task1.py
import sys
import os

# 路径配置，保证识别toolbox包
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

# 工具函数：计算登机口利用率 → 对应Task1指标3
def calc_gate_utilization(gate, total_sim_time):
    if total_sim_time == 0:
        return 0.0
    busy = gate.busy_time if hasattr(gate, "busy_time") else 0
    return round(busy / total_sim_time, 3)

# 核心仿真逻辑，完全匹配Task1全部仿真要求
def simulate_boarding(gates, flights, passengers):
    missed_conn = 0  # Task1指标2：错过中转旅客总数
    sim_time = 0      # Task1指标1：总登机仿真时长
    max_time = 500    # 仿真上限，防止死循环

    # 给每个登机口初始化忙碌计时，用于利用率计算
    for g in gates.values():
        g.busy_time = 0

    # 构建航班-旅客映射，方便中转校验
    flight_pass_map = {}
    for f in flights.values():
        flight_pass_map[f.flight_id] = []
    for p in passengers:
        flight_pass_map[p.flight.flight_id].append(p)

    # 核心规则：每个时间单位，每个登机口放行1人
    while sim_time < max_time:
        any_boarding = False
        for g in gates.values():
            if g.boarding_queue.size() > 0:
                g.boarding_queue.dequeue()
                g.busy_time += 1
                any_boarding = True
        # 全部登机口无旅客，仿真提前结束
        if not any_boarding:
            break
        sim_time += 1

    # 统计错过中转航班的旅客（指标2）
    for p in passengers:
        if p.connecting_flight_id is None:
            continue
        conn_fid = p.connecting_flight_id
        if conn_fid not in flights:
            missed_conn += 1
            continue
        conn_flight = flights[conn_fid]
        # 仿真总时长超过中转航班计划起飞时间 → 误机
        if sim_time >= int(conn_flight.scheduled_time.split(":")[0]) * 60:
            missed_conn += 1

    # 批量计算所有登机口利用率（指标3）
    util_result = {}
    for gid, g in gates.items():
        util_result[gid] = calc_gate_utilization(g, sim_time)

    return sim_time, missed_conn, util_result

if __name__ == "__main__":
    # 方案2：动态导入，不写在文件顶部，延后加载模块
    data_gen_mod = __import__("toolbox.data_gen", fromlist=[
        "load_gates", "load_flights", "load_passengers", "link_full_system"
    ])
    load_gates = data_gen_mod.load_gates
    load_flights = data_gen_mod.load_flights
    load_passengers = data_gen_mod.load_passengers
    link_full_system = data_gen_mod.link_full_system

    # 加载数据集并完成系统绑定
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    link_full_system(gates, flights, passengers)

    # 运行登机仿真
    total_time, miss_count, gate_util = simulate_boarding(gates, flights, passengers)

    # 输出Task1要求的汇总报告
    print("========== Part2 Task1 登机仿真汇总报告 ==========")
    print(f"1. 全部航班完成登机总时长：{total_time} 时间单位")
    print(f"2. 错过中转衔接航班旅客总数：{miss_count}")
    print("\n3. 各登机口利用率：")
    for gate_id, rate in gate_util.items():
        print(f"{gate_id}：{rate * 100:.1f}%")