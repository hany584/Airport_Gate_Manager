# 放在文件第一行，强制添加项目根目录到Python检索路径
import sys
import os
# 获取当前test4.py上级的顶层项目文件夹
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

import unittest
import os
# 标准绝对导入toolbox
from toolbox.data_gen import (
    generate_all_datasets, load_gates, load_flights, load_passengers,
    init_gate_graph, FLIGHT_CSV, GATE_CSV, PASSENGER_CSV
)

class TestTask4DataGen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 全局一次性生成CSV测试数据集
        generate_all_datasets()

    def test_csv_file_exists(self):
        # 校验三份CSV文件成功生成在项目根目录
        self.assertTrue(os.path.exists(FLIGHT_CSV))
        self.assertTrue(os.path.exists(GATE_CSV))
        self.assertTrue(os.path.exists(PASSENGER_CSV))

    def test_load_gate_data(self):
        gates = load_gates()
        self.assertGreater(len(gates), 0)
        sample_gate = list(gates.values())[0]
        # 校验每个廊桥自动绑定双队列
        self.assertIsNotNone(sample_gate.regular_queue)
        self.assertIsNotNone(sample_gate.priority_queue)

    def test_load_flight_data(self):
        flights = load_flights()
        self.assertGreater(len(flights), 0)
        sample_flight = list(flights.values())[0]
        self.assertIsInstance(sample_flight.passenger_count, int)

    def test_load_passenger_data(self):
        passengers = load_passengers()
        self.assertGreater(len(passengers), 0)

    def test_init_gate_network(self):
        graph = init_gate_graph()
        self.assertGreater(len(graph.gate_nodes), 0)
        print("\n===== Task4测试：生成的廊桥网络图 =====")
        graph.display_graph()

if __name__ == "__main__":
    unittest.main()