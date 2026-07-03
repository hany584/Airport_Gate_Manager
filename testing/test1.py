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

    def test_passenger_priority_score(self):
        # 测试优先级计算函数
        score = self.test_passenger.get_priority_score()
        self.assertEqual(score, 10+50+40+30)

    def test_passenger_group_range(self):
        # 登机组超出1-5抛异常
        with self.assertRaises(ValueError):
            Passenger("P0002", "Tom Hanks", 6, False)

    def test_flight_attr(self):
        self.assertEqual(self.test_flight.flight_id, "CA1234")
        self.assertEqual(self.test_flight.status, FlightStatus.BOARDING)
        self.assertEqual(self.test_flight.delay_minutes, 15)

    def test_gate_attr(self):
        self.assertEqual(self.test_gate.gate_id, "G01")
        self.assertTrue(self.test_gate.is_international)
        self.assertEqual(self.test_gate.capacity, 150)

if __name__ == "__main__":
    unittest.main()