from typing import Dict, List, Tuple, Optional
from toolbox.models import Gate

class DirectedWeightedGraph:
    def __init__(self):
        self.adjacency: Dict[str, Dict[str, int]] = {}
        self.gate_nodes: Dict[str, Gate] = {}

    def add_gate(self, gate: Gate) -> None:
        if gate.gate_id not in self.gate_nodes:
            self.gate_nodes[gate.gate_id] = gate
            self.adjacency[gate.gate_id] = {}

    def remove_gate(self, gate_id: str) -> None:
        if gate_id not in self.gate_nodes:
            return
        del self.gate_nodes[gate_id]
        del self.adjacency[gate_id]
        for start in self.adjacency:
            if gate_id in self.adjacency[start]:
                del self.adjacency[start][gate_id]

    def add_path(self, from_gate_id: str, to_gate_id: str, walk_min: int) -> None:
        if from_gate_id not in self.gate_nodes or to_gate_id not in self.gate_nodes:
            raise ValueError("廊桥不存在")
        if walk_min <= 0:
            raise ValueError("步行时长必须大于0")
        self.adjacency[from_gate_id][to_gate_id] = walk_min

    def remove_path(self, from_gate_id: str, to_gate_id: str) -> None:
        if from_gate_id in self.adjacency and to_gate_id in self.adjacency[from_gate_id]:
            del self.adjacency[from_gate_id][to_gate_id]

    def update_walk_time(self, from_gate_id: str, to_gate_id: str, new_min: int) -> None:
        if from_gate_id not in self.adjacency or to_gate_id not in self.adjacency[from_gate_id]:
            raise ValueError("通道不存在")
        if new_min <= 0:
            raise ValueError("时长必须大于0")
        self.adjacency[from_gate_id][to_gate_id] = new_min

    def _dfs_find_all(self, cur: str, target: str, visited: List[str], path: List[str], res: List[List[str]]):
        visited.append(cur)
        path.append(cur)
        if cur == target:
            res.append(path.copy())
        else:
            for neighbor in self.adjacency[cur]:
                if neighbor not in visited:
                    self._dfs_find_all(neighbor, target, visited, path, res)
        path.pop()
        visited.remove(cur)

    def find_all_paths(self, start: str, end: str) -> List[List[str]]:
        if start not in self.gate_nodes or end not in self.gate_nodes:
            raise ValueError("廊桥ID不存在")
        all_paths = []
        self._dfs_find_all(start, end, [], [], all_paths)
        return all_paths

    def find_shortest_path(self, start: str, end: str) -> Tuple[Optional[List[str]], Optional[int]]:
        if start not in self.gate_nodes or end not in self.gate_nodes:
            raise ValueError("廊桥ID不存在")
        INF = float("inf")
        dist: Dict[str, float] = {g: INF for g in self.gate_nodes}
        prev: Dict[str, Optional[str]] = {g: None for g in self.gate_nodes}
        dist[start] = 0
        unvisited = set(self.gate_nodes.keys())

        while unvisited:
            current = min(unvisited, key=lambda g: dist[g])
            unvisited.remove(current)
            if current == end:
                break
            for neighbor, w in self.adjacency[current].items():
                if dist[current] + w < dist[neighbor]:
                    dist[neighbor] = dist[current] + w
                    prev[neighbor] = current
        if dist[end] == INF:
            return None, None
        route = []
        temp = end
        while temp is not None:
            route.append(temp)
            temp = prev[temp]
        route.reverse()
        return route, int(dist[end])

    def display_graph(self) -> None:
        print("===== 廊桥有向加权图 =====")
        for gid, edges in self.adjacency.items():
            if edges:
                s = ", ".join([f"{t}({v}min)" for t, v in edges.items()])
                print(f"{gid} → {s}")
            else:
                print(f"{gid} → 无通道")