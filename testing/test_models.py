# 【修改点1】文件重命名：原test1.py → test_airport_models.py，符合 test_<feature>.py 规范
import unittest
from toolbox.models import FlightStatus, Flight, Gate, Passenger

class TestTask1Models(unittest.TestCase):
    def setUp(self):
        # 测试前置数据
        self.test_passenger = Passenger(
            passenger_id="P0001",
            name="Emma Watson",
            boarding_group=1,
            has_special_needs=True,
            connecting_flight_id="CA1234"
        )
        self.test_gate = Gate(
            gate_id="G01",
            terminal="T2",
            capacity=150,
            is_international=True
        )
        self.test_flight = Flight(
            flight_id="CA1234",
            airline="Air China",
            origin_or_destination="London",
            scheduled_time="08:30",
            status=FlightStatus.BOARDING,
            gate_id="G01",
            passenger_count=120,
            delay_minutes=15
        )
        # 【修改点2】扩展前置对象：新增非法登机组乘客、ID不匹配航班用于边界测试
        self.bad_low_group_pax = ("P0003", "Jack", 0, False)
        self.mismatch_gate_flight = Flight(
            flight_id="MU5678",
            airline="China Eastern",
            origin_or_destination="Paris",
            scheduled_time="12:00",
            status=FlightStatus.ON_TIME,
            gate_id="G02",
            passenger_count=90
        )

    def test_passenger_priority_score(self):
        # 测试优先级计算函数
        score = self.test_passenger.get_priority_score()
        self.assertEqual(score, 10+50+40+30)
        # 【修改点3】补充多类型乘客优先级边界校验（普通、仅特殊、仅1组、仅转机）
        pax_normal = Passenger("P0004", "Alice", 3, False)
        self.assertEqual(pax_normal.get_priority_score(), 10)
        pax_special_only = Passenger("P0005", "Bob", 4, True)
        self.assertEqual(pax_special_only.get_priority_score(), 60)
        pax_group1_only = Passenger("P0006", "Cathy", 1, False)
        self.assertEqual(pax_group1_only.get_priority_score(), 50)
        pax_connect_only = Passenger("P0007", "David", 5, False, "MU9999")
        self.assertEqual(pax_connect_only.get_priority_score(), 40)

    def test_passenger_group_range(self):
        # 登机组超出1-5抛异常
        with self.assertRaises(ValueError):
            Passenger("P0002", "Tom Hanks", 6, False)
        # 【修改点4】补充下限0非法登机组边界用例
        with self.assertRaises(ValueError):
            Passenger(*self.bad_low_group_pax)
        # 【修改点5】补充合法1-5全部区间遍历校验
        for valid_group in range(1, 6):
            temp_pax = Passenger(f"P00{valid_group}", "Test", valid_group, False)
            self.assertEqual(temp_pax.boarding_group, valid_group)

    def test_flight_attr(self):
        self.assertEqual(self.test_flight.flight_id, "CA1234")
        self.assertEqual(self.test_flight.status, FlightStatus.BOARDING)
        self.assertEqual(self.test_flight.delay_minutes, 15)
        # 【修改点6】补充Flight双向绑定、乘客添加基础逻辑校验
        self.test_flight.add_passenger(self.test_passenger)
        self.assertIn(self.test_passenger, self.test_flight.passengers)
        self.assertEqual(self.test_passenger.flight, self.test_flight)

    def test_gate_attr(self):
        self.assertEqual(self.test_gate.gate_id, "G01")
        self.assertTrue(self.test_gate.is_international)
        self.assertEqual(self.test_gate.capacity, 150)

    # 【修改点7】新增边界测试：Gate与Flight ID不匹配绑定时抛出异常
    def test_gate_flight_mismatch_bind_error(self):
        with self.assertRaises(ValueError):
            self.test_gate.dock_flight(self.mismatch_gate_flight)
        with self.assertRaises(ValueError):
            self.mismatch_gate_flight.bind_gate(self.test_gate)

    # 【修改点8】新增双向绑定同步逻辑测试：dock_flight自动双向关联
    def test_flight_gate_binding_sync(self):
        self.test_gate.dock_flight(self.test_flight)
        self.assertEqual(self.test_gate.docked_flight, self.test_flight)
        self.assertEqual(self.test_flight.gate, self.test_gate)

    # 【修改点9】新增边界测试：航班未绑定Gate时添加乘客，不会写入队列
    def test_add_passenger_no_gate_no_enqueue(self):
        empty_gate_queue_size = self.test_gate.boarding_queue.size()
        self.test_flight.add_passenger(self.test_passenger)
        self.assertEqual(self.test_gate.boarding_queue.size(), empty_gate_queue_size)

if __name__ == "__main__":
    unittest.main()