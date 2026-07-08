# 修改点1：文件重命名，原test3.py → test_gate_graph.py，符合 test_<feature>.py 规范
import unittest
from toolbox.models import Gate, Flight, FlightStatus
from toolbox.graph import DirectedWeightedGraph

class TestTask3Graph(unittest.TestCase):
    def setUp(self):
        self.g1 = Gate("G01", "T1", 100, False)
        self.g2 = Gate("G02", "T1", 120, False)
        self.g3 = Gate("G03", "T2", 160, True)
        # 修改点2：新增单向走廊测试登机口（单向路径G04→G05，反向无通道）用于有向图边界测试
        self.g4 = Gate("G04", "T1", 80, False)
        self.g5 = Gate("G05", "T1", 90, False)
        # 修改点3：构造测试航班，用于 shortest_path_between_flights 新接口测试
        self.flight_g1 = Flight("F001", "MU", "SHA-PEK", "09:00", FlightStatus.ON_TIME, "G01", 80)
        self.flight_g3 = Flight("F002", "CZ", "PEK-CAN", "11:00", FlightStatus.DELAYED, "G03", 95)
        self.graph = DirectedWeightedGraph()
        # 批量添加所有登机口节点
        self.graph.add_gate(self.g1)
        self.graph.add_gate(self.g2)
        self.graph.add_gate(self.g3)
        self.graph.add_gate(self.g4)
        self.graph.add_gate(self.g5)
        # 基础单向路径 G01→G02(3min), G01→G03(10min), G02→G03(4min)
        self.graph.add_path("G01", "G02", 3)
        self.graph.add_path("G01", "G03", 10)
        self.graph.add_path("G02", "G03", 4)
        # 单向通道：仅G04→G05，无反向通路，用于验证有向图特性
        self.graph.add_path(self.g4, self.g5, 2)
        # 绑定航班与对应登机口
        self.g1.dock_flight(self.flight_g1)
        self.g3.dock_flight(self.flight_g3)

    def test_gate_add_remove(self):
        self.assertIn("G01", self.graph.gate_nodes)
        self.graph.remove_gate("G02")
        self.assertNotIn("G02", self.graph.gate_nodes)
        self.assertNotIn("G02", self.graph.adjacency["G01"])
        # 修改点4：补充传入Gate对象删除节点的重载方法测试
        self.graph.add_gate(self.g2)
        self.graph.remove_gate(self.g2)
        self.assertNotIn("G02", self.graph.gate_nodes)

    def test_path_crud(self):
        # 更新步行时间
        self.graph.update_walk_time("G01", "G02", 5)
        self.assertEqual(self.graph.adjacency["G01"]["G02"], 5)
        # 删除路径
        self.graph.remove_path("G01", "G03")
        self.assertNotIn("G03", self.graph.adjacency["G01"])
        # 修改点5：新增Gate对象入参测试：add_path / remove_path / update_walk_time 重载接口
        self.graph.add_path(self.g1, self.g3, 12)
        self.assertEqual(self.graph.adjacency["G01"]["G03"], 12)
        self.graph.update_walk_time(self.g1, self.g3, 8)
        self.assertEqual(self.graph.adjacency["G01"]["G03"], 8)
        self.graph.remove_path(self.g1, self.g3)
        self.assertNotIn("G03", self.graph.adjacency["G01"])

    def test_path_negative_time_edge_case(self):
        # 修改点6：全新增边界测试：步行时长≤0时抛出异常
        with self.assertRaises(ValueError):
            self.graph.add_path("G01", "G02", 0)
        with self.assertRaises(ValueError):
            self.graph.add_path("G01", "G02", -5)
        with self.assertRaises(ValueError):
            self.graph.update_walk_time("G01", "G02", -2)

    def test_nonexistent_gate_operation(self):
        # 修改点7：全新增边界测试：操作不存在登机口时抛异常
        with self.assertRaises(ValueError):
            self.graph.add_path("G99", "G01", 2)
        with self.assertRaises(ValueError):
            self.graph.find_all_paths("G99", "G02")
        with self.assertRaises(ValueError):
            self.graph.find_shortest_path("G01", "G99")

    def test_all_paths_dfs(self):
        paths = self.graph.find_all_paths("G01", "G03")
        expect_paths = [["G01", "G03"], ["G01", "G02", "G03"]]
        self.assertEqual(len(paths), 2)
        self.assertListEqual(sorted(paths), sorted(expect_paths))
        # 修改点8：补充传入Gate对象查询路径的重载接口测试
        paths_gate_obj = self.graph.find_all_paths(self.g1, self.g3)
        self.assertEqual(len(paths_gate_obj), 2)

    def test_shortest_path_dijkstra(self):
        path, total_time = self.graph.find_shortest_path("G01", "G03")
        self.assertEqual(path, ["G01", "G02", "G03"])
        self.assertEqual(total_time, 3+4)
        # 修改点9：补充Gate对象作为起止点查询最短路径
        path_obj, time_obj = self.graph.find_shortest_path(self.g1, self.g3)
        self.assertEqual(path_obj, ["G01", "G02", "G03"])
        self.assertEqual(time_obj, 7)

    def test_no_path_case(self):
        # 无通路场景
        path, time = self.graph.find_shortest_path("G03", "G01")
        self.assertIsNone(path)
        self.assertIsNone(time)
        # 修改点10：单向有向图边界校验：G04→G05存在，反向G05→G04无通路
        path_rev, time_rev = self.graph.find_shortest_path(self.g5, self.g4)
        self.assertIsNone(path_rev)
        self.assertIsNone(time_rev)

    def test_gate_adjacent_sync_with_graph(self):
        # 修改点11：全新增核心同步测试：图添加/删除边同步更新Gate内部adjacent_gates列表
        # 添加路径后Gate邻接列表自动同步
        self.assertIn(self.g2, self.g1.adjacent_gates)
        self.graph.remove_path(self.g1, self.g2)
        self.assertNotIn(self.g2, self.g1.adjacent_gates)
        # 重新添加，再次校验同步
        self.graph.add_path(self.g1, self.g2, 4)
        self.assertIn(self.g2, self.g1.adjacent_gates)

    def test_link_two_gates_bidirectional(self):
        # 修改点12：新增双向连接工具方法测试 link_two_gates
        self.graph.link_two_gates(self.g4, self.g5, 6)
        # 双向均存在路径
        self.assertIn("G05", self.graph.adjacency["G04"])
        self.assertIn("G04", self.graph.adjacency["G05"])
        # Gate双向邻接同步
        self.assertIn(self.g5, self.g4.adjacent_gates)
        self.assertIn(self.g4, self.g5.adjacent_gates)

    def test_shortest_path_between_flights(self):
        # 修改点13：新增Flight对象跨航班最短路径新接口测试
        path, time = self.graph.shortest_path_between_flights(self.flight_g1, self.flight_g3)
        self.assertEqual(path, ["G01", "G02", "G03"])
        self.assertEqual(time, 7)
        # 边界：未绑定Gate的航班调用该方法抛异常
        empty_flight = Flight("F999", "HU", "HKG-PEK", "14:00", FlightStatus.BOARDING, "G99", 50)
        with self.assertRaises(ValueError):
            self.graph.shortest_path_between_flights(empty_flight, self.flight_g1)

    def test_graph_display_and_gate_full_info(self):
        # 修改点14：新增打印类无异常测试，验证展示方法运行不崩溃
        self.graph.display_graph()
        self.graph.show_gate_full_info("G01")
        # 不存在登机口打印无报错
        self.graph.show_gate_full_info("G99")

if __name__ == "__main__":
    unittest.main()