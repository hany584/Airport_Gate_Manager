from typing import Dict, List, Tuple, Optional
from toolbox.models import Gate, Flight

class DirectedWeightedGraph:
    def __init__(self):
        self.adjacency: Dict[str, Dict[str, int]] = {}
        self.gate_nodes: Dict[str, Gate] = {}

    # ========== 新增重载：支持直接传入Gate对象（不用传gate_id，打通实体与图）==========
    def add_gate(self, gate: Gate) -> None:
        if gate.gate_id not in self.gate_nodes:
            self.gate_nodes[gate.gate_id] = gate
            self.adjacency[gate.gate_id] = {}

    def remove_gate(self, gate_id: str | Gate) -> None:
        # MODIFIED：兼容Gate对象入参，自动提取gate_id
        if isinstance(gate_id, Gate):
            gate_id = gate_id.gate_id
        if gate_id not in self.gate_nodes:
            return
        del self.gate_nodes[gate_id]
        del self.adjacency[gate_id]
        for start in self.adjacency:
            if gate_id in self.adjacency[start]:
                del self.adjacency[start][gate_id]

    # MODIFIED：重载add_path，支持Gate对象参数，同步更新Gate内部adjacent_gates
    def add_path(self, from_gate: str | Gate, to_gate: str | Gate, walk_min: int) -> None:
        # 统一提取gate_id
        from_id = from_gate.gate_id if isinstance(from_gate, Gate) else from_gate
        to_id = to_gate.gate_id if isinstance(to_gate, Gate) else to_gate
        if from_id not in self.gate_nodes or to_id not in self.gate_nodes:
            raise ValueError("廊桥不存在")
        if walk_min <= 0:
            raise ValueError("步行时长必须大于0")
        self.adjacency[from_id][to_id] = walk_min

        # NEW 双向同步Gate内部邻接列表：图添加边 → Gate对象自动记录相邻Gate
        from_gate_obj = self.gate_nodes[from_id]
        to_gate_obj = self.gate_nodes[to_id]
        if to_gate_obj not in from_gate_obj.adjacent_gates:
            from_gate_obj.adjacent_gates.append(to_gate_obj)

    # MODIFIED：重载remove_path，支持Gate对象，同步清理Gate邻接列表
    def remove_path(self, from_gate: str | Gate, to_gate: str | Gate) -> None:
        from_id = from_gate.gate_id if isinstance(from_gate, Gate) else from_gate
        to_id = to_gate.gate_id if isinstance(to_gate, Gate) else to_gate
        if from_id in self.adjacency and to_id in self.adjacency[from_id]:
            del self.adjacency[from_id][to_id]
            # NEW 同步移除Gate内部邻接关系
            from_gate_obj = self.gate_nodes[from_id]
            to_gate_obj = self.gate_nodes[to_id]
            if to_gate_obj in from_gate_obj.adjacent_gates:
                from_gate_obj.adjacent_gates.remove(to_gate_obj)

    # MODIFIED：重载update_walk_time，支持Gate对象入参
    def update_walk_time(self, from_gate: str | Gate, to_gate: str | Gate, new_min: int) -> None:
        from_id = from_gate.gate_id if isinstance(from_gate, Gate) else from_gate
        to_id = to_gate.gate_id if isinstance(to_gate, Gate) else to_gate
        if from_id not in self.adjacency or to_id not in self.adjacency[from_id]:
            raise ValueError("通道不存在")
        if new_min <= 0:
            raise ValueError("时长必须大于0")
        self.adjacency[from_id][to_id] = new_min

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

    # MODIFIED：find_all_paths支持Gate对象作为起止参数
    def find_all_paths(self, start: str | Gate, end: str | Gate) -> List[List[str]]:
        start_id = start.gate_id if isinstance(start, Gate) else start
        end_id = end.gate_id if isinstance(end, Gate) else end
        if start_id not in self.gate_nodes or end_id not in self.gate_nodes:
            raise ValueError("廊桥ID不存在")
        all_paths = []
        self._dfs_find_all(start_id, end_id, [], [], all_paths)
        return all_paths

    # MODIFIED：find_shortest_path支持Gate对象作为起止参数
    def find_shortest_path(self, start: str | Gate, end: str | Gate) -> Tuple[Optional[List[str]], Optional[int]]:
        start_id = start.gate_id if isinstance(start, Gate) else start
        end_id = end.gate_id if isinstance(end, Gate) else end
        if start_id not in self.gate_nodes or end_id not in self.gate_nodes:
            raise ValueError("廊桥ID不存在")
        INF = float("inf")
        dist: Dict[str, float] = {g: INF for g in self.gate_nodes}
        prev: Dict[str, Optional[str]] = {g: None for g in self.gate_nodes}
        dist[start_id] = 0
        unvisited = set(self.gate_nodes.keys())

        while unvisited:
            current = min(unvisited, key=lambda g: dist[g])
            unvisited.remove(current)
            if current == end_id:
                break
            for neighbor, w in self.adjacency[current].items():
                if dist[current] + w < dist[neighbor]:
                    dist[neighbor] = dist[current] + w
                    prev[neighbor] = current
        if dist[end_id] == INF:
            return None, None
        route = []
        temp = end_id
        while temp is not None:
            route.append(temp)
            temp = prev[temp]
        route.reverse()
        return route, int(dist[end_id])

    def display_graph(self) -> None:
        print("===== 廊桥有向加权图 =====")
        for gid, edges in self.adjacency.items():
            gate_obj = self.gate_nodes[gid]
            gate_brief = f"{gate_obj.gate_id}(航站楼:{gate_obj.terminal},容量:{gate_obj.capacity})"
            if edges:
                s = ", ".join([f"{t}({v}min)" for t, v in edges.items()])
                print(f"{gate_brief} → {s}")
            else:
                print(f"{gate_brief} → 无通道")

    def get_gate_by_id(self, gate_id: str) -> Optional[Gate]:
        return self.gate_nodes.get(gate_id)

    # MODIFIED link_two_gates：支持Gate对象，双向同步Gate内部adjacent_gates
    def link_two_gates(self, gate_a: str | Gate, gate_b: str | Gate, walk_time: int) -> None:
        self.add_path(gate_a, gate_b, walk_time)
        self.add_path(gate_b, gate_a, walk_time)

    # ========== 全新新增工具方法（打通图-Flight-登机队列全系统）==========
    # NEW：通过航班直接获取最短步行路径（Flight存Gate对象，无需手动传gate_id）
    def shortest_path_between_flights(self, flight_a: Flight, flight_b: Flight) -> Tuple[Optional[List[str]], Optional[int]]:
        if flight_a.gate is None or flight_b.gate is None:
            raise ValueError("航班未绑定登机口Gate")
        return self.find_shortest_path(flight_a.gate, flight_b.gate)

    # NEW：打印指定登机口关联的航班、登机队列信息，图与业务数据统一展示
    def show_gate_full_info(self, gate_id: str) -> None:
        gate = self.get_gate_by_id(gate_id)
        if gate is None:
            print(f"不存在登机口 {gate_id}")
            return
        print(f"\n=== Gate {gate_id} 完整业务信息 ===")
        print(f"基础信息：航站楼{gate.terminal}，容量{gate.capacity}，国际区：{gate.is_international}")
        print(f"停靠航班：{gate.docked_flight if gate.docked_flight else '无'}")
        print(f"相邻登机口ID：{[g.gate_id for g in gate.adjacent_gates]}")
        print(f"当前排队人数：{gate.boarding_queue.size() if gate.boarding_queue else 0}")
        if gate.boarding_queue:
            gate.boarding_queue.display_all()