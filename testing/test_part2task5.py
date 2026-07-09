# testing/test_parttask5.py
import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from part2.task5 import generate_airport_graph

def test_graph_generation():
    # 测试机场图生成
    graph = generate_airport_graph(n_gates=10, avg_edges=3)
    assert len(graph) == 10
    all_edges = sum(len(v) for v in graph.values())
    assert all_edges > 0

def test_delay_cascade_simulation():
    graph = generate_airport_graph(n_gates=5, avg_edges=2)
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