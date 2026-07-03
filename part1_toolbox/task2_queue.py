from typing import Optional
from part1_toolbox.task1_models import Passenger

# 单链表节点（手写，不使用collections.deque）
class ListNode:
    def __init__(self, value: Passenger):
        self.value = value
        self.next: Optional[ListNode] = None

# FIFO标准队列：链表实现，优于列表list(列表pop(0) O(n)，链表dequeue O(1))
class LinkedListQueue:
    def __init__(self):
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._size = 0

    def enqueue(self, passenger: Passenger) -> None:
        new_node = ListNode(passenger)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def dequeue(self) -> Optional[Passenger]:
        if self.head is None:
            return None
        pop_node = self.head
        self.head = self.head.next
        self._size -= 1
        # 队列为空时尾指针置空
        if self.head is None:
            self.tail = None
        return pop_node.value

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

# 手写最大堆优先队列（不使用heapq库，完全自实现堆结构）
class PriorityQueue:
    def __init__(self):
        self._heap: list[tuple[int, Passenger]] = []

    # 堆索引工具函数
    def _parent_idx(self, idx: int) -> int:
        return (idx - 1) // 2

    def _left_idx(self, idx: int) -> int:
        return 2 * idx + 1

    def _right_idx(self, idx: int) -> int:
        return 2 * idx + 2

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    # 上浮堆化
    def _heapify_up(self, idx: int) -> None:
        parent = self._parent_idx(idx)
        if idx > 0 and self._heap[idx][0] > self._heap[parent][0]:
            self._swap(idx, parent)
            self._heapify_up(parent)

    # 下沉堆化
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
        if len(self._heap) == 0:
            return None
        return self._heap[0][1]

    def size(self) -> int:
        return len(self._heap)

    def display(self) -> None:
        sorted_list = sorted(self._heap, key=lambda x: x[0], reverse=True)
        show_text = [f"{p[1]} (优先级分数:{p[0]})" for p in sorted_list]
        print(f"[优先队列] 排序序列：{' -> '.join(show_text) if show_text else '空队列'}")