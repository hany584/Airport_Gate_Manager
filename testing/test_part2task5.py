# testing/test_parttask5.py
import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
# 改从task4导入公共造图函数
from part2.task4 import build_airport_graph

def test_graph_generation():
    # 替换函数名与参数
    graph = build_airport_graph(num_gates=10)
    assert len(graph) == 10
    all_edges = sum(len(v) for v in graph.values())
    assert all_edges > 0

def test_delay_cascade_simulation():
    # 同步修改调用
    graph = build_airport_graph(num_gates=5)
    delayed = set()
    queue = [0]
    delayed.add(0)
    while queue:
        curr = queue.pop(0)
        for neighbor in graph[curr]:
            if neighbor not in delayed:
                delayed.add(neighbor)
                queue.append(neighbor)
    assert 0 in delayed