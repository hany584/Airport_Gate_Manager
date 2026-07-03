import unittest
from toolbox.models import Passenger
from toolbox.queue import LinkedListQueue, PriorityQueue

class TestTask2Queue(unittest.TestCase):
    def setUp(self):
        # 构造3位不同优先级乘客
        self.p1 = Passenger("P0001", "Emma Watson", 1, True, "CA1001")  # 最高分
        self.p2 = Passenger("P0002", "Jack Smith", 3, False, None)     # 普通
        self.p3 = Passenger("P0003", "Lily Brown", 2, False, "CA2002") # 转机加分
        self.fifo_queue = LinkedListQueue()
        self.pri_queue = PriorityQueue()

    def test_fifo_all_methods(self):
        # 测试FIFO入队、出队、peek、size
        self.fifo_queue.enqueue(self.p1)
        self.fifo_queue.enqueue(self.p2)
        self.assertEqual(self.fifo_queue.size(), 2)
        self.assertEqual(self.fifo_queue.peek(), self.p1)
        out = self.fifo_queue.dequeue()
        self.assertEqual(out, self.p1)
        self.assertEqual(self.fifo_queue.size(), 1)
        self.fifo_queue.dequeue()
        self.assertIsNone(self.fifo_queue.dequeue())

    def test_priority_order(self):
        # 优先队列出队顺序必须按分数从高到低
        self.pri_queue.enqueue(self.p2)
        self.pri_queue.enqueue(self.p1)
        self.pri_queue.enqueue(self.p3)
        self.assertEqual(self.pri_queue.size(), 3)
        first = self.pri_queue.dequeue()
        self.assertEqual(first, self.p1)
        second = self.pri_queue.dequeue()
        self.assertEqual(second, self.p3)
        third = self.pri_queue.dequeue()
        self.assertEqual(third, self.p2)
        self.assertIsNone(self.pri_queue.dequeue())

    def test_queue_display(self):
        # 仅测试无报错，不校验输出文本
        self.fifo_queue.enqueue(self.p1)
        self.fifo_queue.display()
        self.pri_queue.enqueue(self.p3)
        self.pri_queue.display()

if __name__ == "__main__":
    unittest.main()