import unittest
from toolbox.models import Gate
from toolbox.graph import DirectedWeightedGraph

class TestTask3Graph(unittest.TestCase):
    def setUp(self):
        self.g1 = Gate("G01", "T1", 100, False)
        self.g2 = Gate("G02", "T1", 120, False)
        self.g3 = Gate("G03", "T2", 160, True)
        self.graph = DirectedWeightedGraph()
        self.graph.add_gate(self.g1)
        self.graph.add_gate(self.g2)
        self.graph.add_gate(self.g3)
        # 添加单向路径 G01→G02(3min), G01→G03(10min), G02→G03(4min)
        self.graph.add_path("G01", "G02", 3)
        self.graph.add_path("G01", "G03", 10)
        self.graph.add_path("G02", "G03", 4)

    def test_gate_add_remove(self):
        self.assertIn("G01", self.graph.gate_nodes)
        self.graph.remove_gate("G02")
        self.assertNotIn("G02", self.graph.gate_nodes)
        self.assertNotIn("G02", self.graph.adjacency["G01"])

    def test_path_crud(self):
        # 更新步行时间
        self.graph.update_walk_time("G01", "G02", 5)
        self.assertEqual(self.graph.adjacency["G01"]["G02"], 5)
        # 删除路径
        self.graph.remove_path("G01", "G03")
        self.assertNotIn("G03", self.graph.adjacency["G01"])

    def test_all_paths_dfs(self):
        paths = self.graph.find_all_paths("G01", "G03")
        expect_paths = [["G01", "G03"], ["G01", "G02", "G03"]]
        self.assertEqual(len(paths), 2)
        self.assertListEqual(sorted(paths), sorted(expect_paths))

    def test_shortest_path_dijkstra(self):
        path, total_time = self.graph.find_shortest_path("G01", "G03")
        self.assertEqual(path, ["G01", "G02", "G03"])
        self.assertEqual(total_time, 3+4)

    def test_no_path_case(self):
        # 无通路场景
        path, time = self.graph.find_shortest_path("G03", "G01")
        self.assertIsNone(path)
        self.assertIsNone(time)

if __name__ == "__main__":
    unittest.main()