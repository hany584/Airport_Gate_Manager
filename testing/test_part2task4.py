# testing/test_task4.py
import sys
import os

# 配置路径，保证可以导入part2模块
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from part2.task4 import build_airport_graph, bfs_shortest_path


def test_airport_graph_average_degree():
    """测试：生成的机场图平均度数接近3，满足题目要求"""
    graph = build_airport_graph(num_gates=10)
    # 统计总边数
    total_connection = sum(len(neighbors) for neighbors in graph.values())
    avg_degree = total_connection / 10
    # 允许少量随机误差，保证在2.5~3.5之间
    assert 2.5 <= avg_degree <= 3.5


def test_bfs_shortest_path_correct():
    """测试：BFS最短路径计算结果正确"""
    test_graph = {
        0: [1],
        1: [0, 2],
        2: [1]
    }
    dist = bfs_shortest_path(test_graph, start_gate=0, end_gate=2)
    assert dist == 2


def test_benchmark_runs_without_error():
    """测试：计时函数可以正常运行，不报错"""
    graph = build_airport_graph(20)
    # 只要能正常执行走完，就算通过
    from part2.task4 import measure_shortest_path_time
    runtime = measure_shortest_path_time(graph, test_times=5)
    assert runtime >= 0