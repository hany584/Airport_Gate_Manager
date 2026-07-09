import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import os
import random

# 适配项目路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

# 复用task4的图生成、延误扩散函数
from part2.task4 import build_airport_graph, delay_cascade_propagate


# ========== 生成graph变量，解决 graph未定义 问题 ==========
graph = build_airport_graph(num_gates=10)
G = nx.from_dict_of_lists(graph)

# 固定布局，防止动画节点乱跳
pos = nx.spring_layout(G, seed=42)
fig, ax = plt.subplots(figsize=(10, 7))

# 延误仿真数据
delayed_nodes = set()
delay_queue = []
step_counter = 0
# 手动设置初始延误登机口
start_delay_gate = 0
delay_queue.append(start_delay_gate)
delayed_nodes.add(start_delay_gate)

# 动画更新函数
def update(frame):
    global step_counter, delayed_nodes, delay_queue
    ax.clear()

    # 单步传播延误
    if delay_queue:
        current = delay_queue.pop(0)
        # 遍历相邻登机口，扩散延误
        for neighbor in graph[current]:
            if neighbor not in delayed_nodes:
                delayed_nodes.add(neighbor)
                delay_queue.append(neighbor)

    # 节点上色：红色延误，灰色正常
    node_colors = ["#ff4444" if node in delayed_nodes else "#cccccc" for node in G.nodes()]
    nx.draw(G, pos, ax=ax, node_color=node_colors, with_labels=True, node_size=800)
    # 边权重代表步行时间
    edge_weight = {(u, v): 2 for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_weight, ax=ax)

    ax.set_title(f"Delay Cascade Animation | Step {step_counter} | Delayed Gates: {sorted(delayed_nodes)}")
    step_counter += 1

# 启动动画，共20步，每步间隔1秒
ani = FuncAnimation(fig, update, frames=20, interval=1000, repeat=False)
plt.tight_layout()
plt.show()