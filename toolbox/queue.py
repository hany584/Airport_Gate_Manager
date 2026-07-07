from typing import Optional
from toolbox.models import Passenger

# 单链表节点（完全保留原始代码，无任何修改）
class ListNode:
    def __init__(self, value: Passenger):
        self.value = value
        self.next: Optional[ListNode] = None

# FIFO链表队列【按需求改造：内置堆，单向同步，无循环调用】
class LinkedListQueue:
    def __init__(self):
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._size = 0
        # 改进1：内部实例化优先堆，由FIFO单向管理堆，禁止反向操作
        self._priority_heap = PriorityQueue()

    def enqueue(self, passenger: Passenger) -> None:
        # 原有FIFO入队逻辑完整保留
        new_node = ListNode(passenger)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1
        # 改进2：入队后单向同步更新堆，堆不会回调队列，无循环调用
        self._priority_heap.enqueue(passenger)

    def dequeue(self) -> Optional[Passenger]:
        if self.head is None:
            return None
        # 原有FIFO出队逻辑完整保留
        pop_node = self.head
        self.head = self.head.next
        self._size -= 1
        if self.head is None:
            self.tail = None
        removed_pax = pop_node.value

        # 改进3：出队后重建堆，仅读取FIFO数据更新堆，单向同步
        self._priority_heap = PriorityQueue()
        cur = self.head
        while cur:
            self._priority_heap.enqueue(cur.value)
            cur = cur.next
        return removed_pax

    def peek(self) -> Optional[Passenger]:
        return self.head.value if self.head else None

    def size(self) -> int:
        return self._size

    def display(self) -> None:
        cur = self.head
        res = []
        while cur:
            res.append(str(cur.value))
            cur = cur.next
        print(f"[FIFO队列] 元素：{' -> '.join(res) if res else '空队列'}")

    # 改进4：新增对外展示堆视图的方法，仅可读、不可修改堆
    def display_priority_view(self):
        self._priority_heap.display()

    # 改进5：新增一致性校验方法，满足测试中FIFO与堆同步校验需求
    def check_coherence(self) -> bool:
        fifo_ids = set()
        cur = self.head
        while cur:
            fifo_ids.add(cur.value.pid)
            cur = cur.next
        heap_items = self._priority_heap.get_all_items()
        heap_ids = set(item[1].pid for item in heap_items)
        return fifo_ids == heap_ids

# 最大堆优先队列（原有堆逻辑全部保留，仅新增辅助方法）
class PriorityQueue:
    def __init__(self):
        self._heap: list[tuple[int, Passenger]] = []

    def _parent_idx(self, idx: int) -> int:
        return (idx - 1) // 2

    def _left_idx(self, idx: int) -> int:
        return 2 * idx + 1

    def _right_idx(self, idx: int) -> int:
        return 2 * idx + 2

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _heapify_up(self, idx: int) -> None:
        parent = self._parent_idx(idx)
        if idx > 0 and self._heap[idx][0] > self._heap[parent][0]:
            self._swap(idx, parent)
            self._heapify_up(parent)

    def _heapify_down(self, idx: int) -> None:
        largest = idx
        left = self._left_idx(idx)
        right = self._right_idx(idx)
        if left < len(self._heap) and self._heap[left][0] > self._heap[largest][0]:
            largest = left
        if right < len(self._heap) and self._heap[right][0] > self._heap[largest][0]:
            largest = right
        if largest != idx:
            self._swap(idx, largest)
            self._heapify_down(largest)

    def enqueue(self, passenger: Passenger) -> None:
        score = passenger.get_priority_score()
        self._heap.append((score, passenger))
        self._heapify_up(len(self._heap)-1)

    def dequeue(self) -> Optional[Passenger]:
        if len(self._heap) == 0:
            return None
        self._swap(0, len(self._heap)-1)
        top_score, top_person = self._heap.pop()
        self._heapify_down(0)
        return top_person

    def peek(self) -> Optional[Passenger]:
        return self._heap[0][1] if self._heap else None

    def size(self) -> int:
        return len(self._heap)

    def display(self) -> None:
        sorted_list = sorted(self._heap, key=lambda x: x[0], reverse=True)
        show_text = [f"{p[1]} (分数:{p[0]})" for p in sorted_list]
        print(f"[优先队列] 排序：{' -> '.join(show_text) if show_text else '空队列'}")

    # 改进6：新增读取堆全部元素的辅助方法，供一致性校验使用
    def get_all_items(self) -> list[tuple[int, Passenger]]:
        return self._heap.copy()