from typing import Dict, List, Tuple, Optional
from part1_toolbox.task1_models import Gate

class DirectedWeightedGraph:
    def __init__(self):
        # 邻接表：{起点登机口: {终点登机口: 步行分钟数}}
        self.adjacency: Dict[str, Dict[str, int]] = {}
        # 存储所有登机口节点对象
        self.gate_nodes: Dict[str, Gate] = {}

    # 节点操作：增删登机口
    def add_gate(self, gate: Gate) -> None:
        if gate.gate_id not in self.gate_nodes:
            self.gate_nodes[gate.gate_id] = gate
            self.adjacency[gate.gate_id] = {}

    def remove_gate(self, gate_id: str) -> None:
        if gate_id not in self.gate_nodes:
            return
        # 删除节点
        del self.gate_nodes[gate_id]
        del self.adjacency[gate_id]
        # 删除所有指向该节点的边
        for start in self.adjacency:
            if gate_id in self.adjacency[start]:
                del self.adjacency[start][gate_id]

    # 边操作：增删改路径
    def add_path(self, from_gate_id: str, to_gate_id: str, walk_min: int) -> None:
        if from_gate_id not in self.gate_nodes or to_gate_id not in self.gate_nodes:
            raise ValueError("不存在该登机口节点")
        if walk_min <= 0:
            raise ValueError("步行时间必须大于0分钟")
        self.adjacency[from_gate_id][to_gate_id] = walk_min

    def remove_path(self, from_gate_id: str, to_gate_id: str) -> None:
        if from_gate_id in self.adjacency and to_gate_id in self.adjacency[from_gate_id]:
            del self.adjacency[from_gate_id][to_gate_id]

    def update_walk_time(self, from_gate_id: str, to_gate_id: str, new_min: int) -> None:
        if from_gate_id not in self.adjacency or to_gate_id not in self.adjacency[from_gate_id]:
            raise ValueError("该路径不存在")
        if new_min <= 0:
            raise ValueError("步行时间必须大于0分钟")
        self.adjacency[from_gate_id][to_gate_id] = new_min

    # DFS 查找两点间全部路径
    def _dfs_find_all(self, cur: str, target: str, visited: List[str], path: List[str], result: List[List[str]]):
        visited.append(cur)
        path.append(cur)
        if cur == target:
            result.append(path.copy())
        else:
            for neighbor in self.adjacency[cur]:
                if neighbor not in visited:
                    self._dfs_find_all(neighbor, target, visited, path, result)
        path.pop()
        visited.remove(cur)

    def find_all_paths(self, start_gate: str, end_gate: str) -> List[List[str]]:
        if start_gate not in self.gate_nodes or end_gate not in self.gate_nodes:
            raise ValueError("登机口不存在")
        all_paths = []
        self._dfs_find_all(start_gate, end_gate, [], [], all_paths)
        return all_paths

    # Dijkstra 求最短路径（非负权重最优算法，优于暴力DFS）
    def find_shortest_path(self, start_gate: str, end_gate: str) -> Tuple[Optional[List[str]], Optional[int]]:
        if start_gate not in self.gate_nodes or end_gate not in self.gate_nodes:
            raise ValueError("登机口不存在")
        INF = float("inf")
        dist: Dict[str, float] = {g: INF for g in self.gate_nodes}
        prev: Dict[str, Optional[str]] = {g: None for g in self.gate_nodes}
        dist[start_gate] = 0
        unvisited = set(self.gate_nodes.keys())

        while unvisited:
            # 选取当前距离最小节点
            current = min(unvisited, key=lambda g: dist[g])
            unvisited.remove(current)
            if current == end_gate:
                break
            # 松弛更新邻接点
            for neighbor, weight in self.adjacency[current].items():
                if dist[current] + weight < dist[neighbor]:
                    dist[neighbor] = dist[current] + weight
                    prev[neighbor] = current
        # 无通路
        if dist[end_gate] == INF:
            return None, None
        # 反向回溯构建路径
        route = []
        temp = end_gate
        while temp is not None:
            route.append(temp)
            temp = prev[temp]
        return route[::-1], int(dist[end_gate])

    def display_graph(self) -> None:
        print("===== 登机口有向加权图 =====")
        for gate_id, edges in self.adjacency.items():
            if edges:
                edge_text = ", ".join([f"{to}({t}min)" for to, t in edges.items()])
                print(f"{gate_id} → {edge_text}")
            else:
                print(f"{gate_id} → 无向外路径")