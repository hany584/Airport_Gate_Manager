# part2/task4.py
import random
import time
import matplotlib.pyplot as plt
from collections import deque

# ==============================================
# 步骤1：生成机场拓扑图（V个顶点，平均每个节点3条边）
# ==============================================
def build_airport_graph(num_gates):
    """
    功能：生成登机口连通无向图
    输入：num_gates 登机口总数量N
    约束：每个登机口平均3条双向通道
    """
    graph = {i: [] for i in range(num_gates)}  # 邻接表存储机场图
    edge_set = set()  # 防止生成重复双向边
    total_target_edges = int((num_gates * 3) / 2)  # 无向图总边数公式

    # 不断随机加边，直到边数达标
    while len(edge_set) < total_target_edges:
        u = random.randint(0, num_gates - 1)  # 随机起点登机口
        v = random.randint(0, num_gates - 1)  # 随机终点登机口
        if u != v and (u, v) not in edge_set and (v, u) not in edge_set:
            edge_set.add((u, v))
            graph[u].append(v)
            graph[v].append(u)
    return graph

# ==============================================
# 步骤2-1：任务1 最短路径 + 计时函数
# ==============================================
def bfs_shortest_path(graph, start_gate, end_gate):
    """BFS计算两个登机口之间最短步行路径"""
    if start_gate == end_gate:
        return 0
    visited = {start_gate}
    queue = deque([(start_gate, 0)])
    while queue:
        current_node, dist = queue.popleft()
        for neighbor in graph[current_node]:
            if neighbor == end_gate:
                return dist + 1
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return None

def measure_shortest_path_time(graph, test_times=20):
    """多次随机选取登机口对，批量运行寻路，统计总耗时"""
    node_list = list(graph.keys())
    start_time = time.perf_counter()  # 高精度计时开始
    for _ in range(test_times):
        gate_a, gate_b = random.sample(node_list, 2)
        bfs_shortest_path(graph, gate_a, gate_b)
    total_time = time.perf_counter() - start_time  # 计算总运行时长
    return total_time

# ==============================================
# 步骤2-2：任务2 延误级联传播 + 计时函数
# ==============================================
def delay_cascade_propagate(graph, source_gate=0):
    """从初始延误节点出发，BFS逐层扩散连锁延误"""
    delayed_set = set()
    queue = deque([source_gate])
    delayed_set.add(source_gate)
    while queue:
        curr = queue.popleft()
        for neighbour in graph[curr]:
            if neighbour not in delayed_set:
                delayed_set.add(neighbour)
                queue.append(neighbour)
    return delayed_set

def measure_cascade_time(graph):
    """测量单次完整延误级联仿真的运行时间"""
    start_time = time.perf_counter()
    delay_cascade_propagate(graph, source_gate=0)
    run_time = time.perf_counter() - start_time
    return run_time

# ==============================================
# 步骤2-3：任务3 登机仿真 + 计时函数
# ==============================================
def boarding_simulation(flight_num, passenger_per_flight):
    """模拟N架航班、每架M名乘客的完整登机排队逻辑"""
    total_passengers = flight_num * passenger_per_flight
    passenger_queue = list(range(total_passengers))
    passenger_queue.sort()  # 用队列运算模拟登机流程开销

def measure_boarding_time(gate_count):
    """按当前机场规模生成航班数据，运行登机仿真并计时"""
    flight_count = gate_count       # 航班数量 = 登机口数量N
    m_passengers = 15               # 每架航班乘客数量M
    start_time = time.perf_counter()
    boarding_simulation(flight_count, m_passengers)
    return time.perf_counter() - start_time

# ==============================================
# 步骤3：循环遍历5组规模，批量采集耗时数据
# ==============================================
def run_full_benchmark():
    # 题目指定的5档机场规模
    scale_list = [10, 50, 200, 500, 1000]
    time_path = []        # 存放每一档N对应的最短路径耗时
    time_cascade = []      # 存放每一档N对应的延误传播耗时
    time_boarding = []     # 存放每一档N对应的登机仿真耗时

    # 循环逐个规模执行压力测试
    for N in scale_list:
        print(f"正在执行 N = {N} 的基准测试")
        airport_graph = build_airport_graph(N)  # 生成当前规模机场模型

        t1 = measure_shortest_path_time(airport_graph)
        t2 = measure_cascade_time(airport_graph)
        t3 = measure_boarding_time(N)

        time_path.append(t1)
        time_cascade.append(t2)
        time_boarding.append(t3)

    # ==============================================
    # 步骤4：matplotlib绘制三条性能曲线
    # ==============================================
    plt.figure(figsize=(10, 6))
    plt.plot(scale_list, time_path, marker="o", label="Shortest Path Calculation")
    plt.plot(scale_list, time_cascade, marker="s", label="Delay Cascade Propagation")
    plt.plot(scale_list, time_boarding, marker="^", label="Boarding Simulation")

    plt.xlabel("Number of Gates N")
    plt.ylabel("Program Runtime (seconds)")
    plt.title("Task 4 Empirical Benchmarking")
    plt.legend()
    plt.grid(True)
    plt.show()

    # 打印表格数据，用于作业分析
    print("\n===== 运行耗时数据表 =====")
    for idx, n in enumerate(scale_list):
        print(f"N={n:4d} | Path:{time_path[idx]:.5f}s | Cascade:{time_cascade[idx]:.5f}s | Boarding:{time_boarding[idx]:.5f}s")

if __name__ == "__main__":
    run_full_benchmark()