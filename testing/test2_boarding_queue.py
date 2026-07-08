# 修改点1：文件重命名，原test2.py → test_boarding_queue.py，符合 test_<feature>.py 规范
import unittest
from toolbox.models import Passenger
from toolbox.queue import LinkedListQueue, PriorityQueue

class TestTask2Queue(unittest.TestCase):
    def setUp(self):
        # 构造3位不同优先级乘客
        self.p1 = Passenger("P0001", "Emma Watson", 1, True, "CA1001")  # 最高分
        self.p2 = Passenger("P0002", "Jack Smith", 3, False, None)     # 普通
        self.p3 = Passenger("P0003", "Lily Brown", 2, False, "CA2002") # 转机加分
        # 修改点2：新增3名完全相同优先级乘客，用于相等优先级边界测试
        self.eq_p1 = Passenger("P_EQ01", "A", 1, True, "F001")
        self.eq_p2 = Passenger("P_EQ02", "B", 1, True, "F001")
        self.eq_p3 = Passenger("P_EQ03", "C", 1, True, "F001")
        
        self.fifo_queue = LinkedListQueue()
        self.pri_queue = PriorityQueue()

    def test_empty_queue_edge_cases(self):
        # 修改点3：全新增空队列边界用例，覆盖题目要求empty queue场景
        empty_q = LinkedListQueue()
        # 空队列size为0
        self.assertEqual(empty_q.size(), 0)
        # 空队列peek返回None
        self.assertIsNone(empty_q.peek())
        # 空队列dequeue返回None，无崩溃
        self.assertIsNone(empty_q.dequeue())
        # 空队列display_all无报错
        empty_q.display_all()

        empty_pri = PriorityQueue()
        self.assertEqual(empty_pri.size(), 0)
        self.assertIsNone(empty_pri.peek())
        self.assertIsNone(empty_pri.dequeue())
        empty_pri.display()

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

    def test_equal_priority_fifo_rule(self):
        # 修改点4：全新增相等优先级测试，满足题目equal priorities需求
        same_score_queue = LinkedListQueue()
        # 同优先级乘客依次入队
        same_score_queue.enqueue(self.eq_p1)
        same_score_queue.enqueue(self.eq_p2)
        same_score_queue.enqueue(self.eq_p3)
        # 同优先级必须严格遵循FIFO入队顺序出队
        self.assertEqual(same_score_queue.dequeue(), self.eq_p1)
        self.assertEqual(same_score_queue.dequeue(), self.eq_p2)
        self.assertEqual(same_score_queue.dequeue(), self.eq_p3)

    def test_fifo_heap_coherent_sync(self):
        # 修改点5：全新增核心测试，校验FIFO链表与内置堆时刻数据一致
        sync_q = LinkedListQueue()
        test_passengers = [self.p1, self.p2, self.p3, self.eq_p1, self.eq_p2]
        # 每一次入队后校验两边元素完全相同
        for pax in test_passengers:
            sync_q.enqueue(pax)
            heap = sync_q.get_priority_queue()
            # 提取两边乘客ID集合对比
            fifo_ids = set()
            cur = sync_q.head
            while cur:
                fifo_ids.add(cur.value.passenger_id)
                cur = cur.next
            heap_ids = set(item[1].passenger_id for item in heap._heap)
            self.assertEqual(fifo_ids, heap_ids, f"入队{pax.passenger_id}后FIFO与堆数据不一致")
        
        # 循环出队，每次出队后同步校验一致性
        while sync_q.size() > 0:
            sync_q.dequeue()
            heap = sync_q.get_priority_queue()
            fifo_ids = set()
            cur = sync_q.head
            while cur:
                fifo_ids.add(cur.value.passenger_id)
                cur = cur.next
            heap_ids = set(item[1].passenger_id for item in heap._heap)
            self.assertEqual(fifo_ids, heap_ids, "出队后FIFO与堆数据不一致")
        # 全部清空后两边都无数据
        self.assertEqual(sync_q.size(), 0)
        self.assertEqual(sync_q.get_priority_queue().size(), 0)

    def test_queue_display(self):
        # 仅测试无报错，不校验输出文本
        self.fifo_queue.enqueue(self.p1)
        self.fifo_queue.display()
        self.pri_queue.enqueue(self.p3)
        self.pri_queue.display()
        # 修改点6：新增display_all接口测试，验证同步打印功能无异常
        self.fifo_queue.display_all()

if __name__ == "__main__":
    unittest.main()