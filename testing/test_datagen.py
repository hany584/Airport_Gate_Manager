# 修改点1：文件重命名，原test4.py → test_dataset_generator.py，符合 test_<feature>.py 命名规范
# 第一层路径兜底：测试文件运行时注入项目根目录
import sys
import os
test_file_dir = os.path.dirname(__file__)
# 项目顶层文件夹 = test_dataset_generator.py上级目录
project_root = os.path.abspath(os.path.join(test_file_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 基础库导入
import unittest
import os

# 标准绝对导入toolbox，无相对导入
from toolbox.data_gen import (
    generate_all_datasets, load_gates, load_flights, load_passengers,
    init_gate_graph, link_full_system, check_queue_coherence,
    FLIGHT_CSV, GATE_CSV, PASSENGER_CSV, generate_project_documents
)
from toolbox.models import Gate, Flight, Passenger

class TestTask4DataGen(unittest.TestCase):
    # 所有测试执行前全局生成CSV文件
    @classmethod
    def setUpClass(cls):
        generate_all_datasets()
        # 修改点2：全局一次性加载完整数据集，用于全链路联动测试复用
        cls.gate_map = load_gates()
        cls.flight_map = load_flights()
        cls.pax_list = load_passengers()
        # 修改点3：执行全系统联动绑定，模拟真实业务关联关系
        link_full_system(cls.gate_map, cls.flight_map, cls.pax_list)

    def test_csv_file_exists(self):
        """校验三份CSV文件成功生成在项目根目录"""
        self.assertTrue(os.path.exists(FLIGHT_CSV))
        self.assertTrue(os.path.exists(GATE_CSV))
        self.assertTrue(os.path.exists(PASSENGER_CSV))
        # 修改点4：新增空文件边界校验，确保CSV不为空白
        self.assertGreater(os.path.getsize(FLIGHT_CSV), 10)
        self.assertGreater(os.path.getsize(GATE_CSV), 10)
        self.assertGreater(os.path.getsize(PASSENGER_CSV), 10)

    def test_load_gate_with_queue(self):
        """校验廊桥加载，自动绑定同步一体化FIFO队列"""
        gates = self.gate_map
        self.assertGreater(len(gates), 0)
        sample_gate = list(gates.values())[0]
        self.assertIsNotNone(sample_gate.boarding_queue)
        # 修改点5：校验Gate队列初始为空边界
        self.assertEqual(sample_gate.boarding_queue.size(), 0)

    def test_load_flight_object(self):
        """校验航班数据正常实例化"""
        flights = self.flight_map
        self.assertGreater(len(flights), 0)
        # 修改点6：校验航班成功双向绑定对应Gate实体
        sample_flight = list(flights.values())[0]
        target_gate = self.gate_map[sample_flight._gate_id]
        self.assertEqual(sample_flight.gate, target_gate)
        self.assertEqual(target_gate.docked_flight, sample_flight)

    def test_load_passenger_object(self):
        """校验旅客数据正常实例化"""
        passengers = self.pax_list
        self.assertGreater(len(passengers), 0)
        # 修改点7：校验乘客完成与航班双向绑定，存在关联航班
        sample_pax = passengers[0]
        self.assertIsNotNone(sample_pax.flight)
        self.assertIn(sample_pax, sample_pax.flight.passengers)

    def test_init_gate_network_graph(self):
        """校验从CSV数据初始化完整廊桥网络图"""
        graph = init_gate_graph()
        self.assertGreater(len(graph.gate_nodes), 0)
        # 修改点8：校验图节点与加载的Gate集合完全匹配
        self.assertEqual(set(graph.gate_nodes.keys()), set(self.gate_map.keys()))
        print("\n===== Task4测试输出：廊桥步行网络图 =====")
        graph.display_graph()

    # 修改点9：全新增边界测试：空数据集生成（0个登机口/航班/乘客）
    def test_empty_dataset_generation_edge(self):
        from toolbox.data_gen import generate_gates_csv, generate_flights_csv, generate_passengers_csv
        generate_gates_csv(gate_num=0)
        generate_flights_csv(flight_num=0)
        generate_passengers_csv(pass_num=0)
        # 空文件可正常读取不崩溃
        empty_gates = load_gates()
        empty_flights = load_flights()
        empty_pax = load_passengers()
        self.assertEqual(len(empty_gates), 0)
        self.assertEqual(len(empty_flights), 0)
        self.assertEqual(len(empty_pax), 0)
        # 恢复标准数据集
        generate_all_datasets()

    # 修改点10：全新增核心一致性测试：全链路校验FIFO与堆同步，匹配题干需求
    def test_all_linked_queue_fifo_heap_coherent(self):
        """全系统联动后，遍历所有登机口队列，校验FIFO链表与内部堆数据时刻一致"""
        for gate in self.gate_map.values():
            queue = gate.boarding_queue
            # 校验同步工具函数返回True
            self.assertEqual(check_queue_coherence(queue), True,
                             f"Gate {gate.gate_id} 的FIFO与优先堆数据不一致")
            # 出队一次后再次校验同步
            if queue.size() > 0:
                queue.dequeue()
                self.assertEqual(check_queue_coherence(queue), True,
                                 f"Gate {gate.gate_id} 出队后FIFO与堆数据不一致")

    # 修改点11：新增项目文档生成测试，验证requirements.txt、README生成无报错
    def test_project_doc_generate(self):
        generate_project_documents()
        self.assertTrue(os.path.exists(os.path.join(project_root, "requirements.txt")))
        self.assertTrue(os.path.exists(os.path.join(project_root, "README.md")))

# 单独运行本测试文件入口
if __name__ == "__main__":
    unittest.main()