from typing import Dict, List, Tuple, Optional
from toolbox.models import Gate

class DirectedWeightedGraph:
    def __init__(self):
        self.adjacency: Dict[str, Dict[str, int]] = {}
        # 改进1：gate_nodes 存储 Gate 完整对象，绑定图与Gate实体，而非仅ID映射
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
            # 改进2：打印时输出Gate完整对象信息，打通图与Gate实体展示，统一系统视图
            gate_obj = self.gate_nodes[gid]
            gate_brief = f"{gate_obj.gate_id}(航站楼:{gate_obj.terminal},容量:{gate_obj.capacity})"
            if edges:
                s = ", ".join([f"{t}({v}min)" for t, v in edges.items()])
                print(f"{gate_brief} → {s}")
            else:
                print(f"{gate_brief} → 无通道")

    # 改进3：新增方法，通过gate_id获取完整Gate对象，实现图系统直接操作Gate实体（匹配任务2：图与数据联动）
    def get_gate_by_id(self, gate_id: str) -> Optional[Gate]:
        return self.gate_nodes.get(gate_id)

    # 改进4：新增批量绑定登机口邻接关系的工具方法，快速构建机场完整拓扑图
    def link_two_gates(self, gate_a_id: str, gate_b_id: str, walk_time: int) -> None:
        self.add_path(gate_a_id, gate_b_id, walk_time)
        self.add_path(gate_b_id, gate_a_id, walk_time)