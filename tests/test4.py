import unittest
import os
from part1_toolbox.task4_data_gen import (
    generate_all_datasets, load_gates, load_flights, load_passengers,
    init_gate_graph, FLIGHT_CSV, GATE_CSV, PASSENGER_CSV
)

class TestTask4DataGen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 生成测试数据集
        generate_all_datasets()

    def test_csv_file_exists(self):
        # 校验CSV文件生成到根目录
        self.assertTrue(os.path.exists(FLIGHT_CSV))
        self.assertTrue(os.path.exists(GATE_CSV))
        self.assertTrue(os.path.exists(PASSENGER_CSV))

    def test_load_gate_data(self):
        gates = load_gates()
        self.assertGreater(len(gates), 0)
        sample_gate = list(gates.values())[0]
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
        sample_p = passengers[0]
        self.assertIsInstance(sample_p.boarding_group, int)

    def test_init_graph_from_csv(self):
        graph = init_gate_graph()
        self.assertGreater(len(graph.gate_nodes), 0)
        graph.display_graph()

if __name__ == "__main__":
    unittest.main()