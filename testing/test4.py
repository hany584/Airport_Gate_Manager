# 第一层路径兜底：测试文件运行时注入项目根目录
import sys
import os
test_file_dir = os.path.dirname(__file__)
# 项目顶层文件夹 = test4.py上级目录
project_root = os.path.abspath(os.path.join(test_file_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 基础库导入
import unittest
import os

# 标准绝对导入toolbox，无相对导入
from toolbox.data_gen import (
    generate_all_datasets, load_gates, load_flights, load_passengers,
    init_gate_graph, FLIGHT_CSV, GATE_CSV, PASSENGER_CSV
)

class TestTask4DataGen(unittest.TestCase):
    # 所有测试执行前全局生成CSV文件
    @classmethod
    def setUpClass(cls):
        generate_all_datasets()

    def test_csv_file_exists(self):
        """校验三份CSV文件成功生成在项目根目录"""
        self.assertTrue(os.path.exists(FLIGHT_CSV))
        self.assertTrue(os.path.exists(GATE_CSV))
        self.assertTrue(os.path.exists(PASSENGER_CSV))

    def test_load_gate_with_queue(self):
        """校验廊桥加载，自动绑定FIFO、优先队列"""
        gates = load_gates()
        self.assertGreater(len(gates), 0)
        sample_gate = list(gates.values())[0]
        self.assertIsNotNone(sample_gate.regular_queue)
        self.assertIsNotNone(sample_gate.priority_queue)

    def test_load_flight_object(self):
        """校验航班数据正常实例化"""
        flights = load_flights()
        self.assertGreater(len(flights), 0)

    def test_load_passenger_object(self):
        """校验旅客数据正常实例化"""
        passengers = load_passengers()
        self.assertGreater(len(passengers), 0)

    def test_init_gate_network_graph(self):
        """校验从CSV数据初始化完整廊桥网络图"""
        graph = init_gate_graph()
        self.assertGreater(len(graph.gate_nodes), 0)
        print("\n===== Task4测试输出：廊桥步行网络图 =====")
        graph.display_graph()

# 单独运行本测试文件入口
if __name__ == "__main__":
    unittest.main()