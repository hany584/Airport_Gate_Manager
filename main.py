from part1_toolbox.task4_data_gen import generate_all_datasets, load_gates, load_flights, load_passengers, init_gate_graph
from part1_toolbox.task2_queue import LinkedListQueue, PriorityQueue
from part1_toolbox.task1_models import Passenger

def demo_queue_function():
    """演示两种队列使用"""
    print("\n===== 队列功能演示 =====")
    p1 = Passenger("P0001", "Olivia Taylor", 1, True, "CA9999")
    p2 = Passenger("P0002", "Noah Wilson", 4, False, None)
    p3 = Passenger("P0003", "Ava Davis", 2, False, "CA8888")

    fifo = LinkedListQueue()
    fifo.enqueue(p1)
    fifo.enqueue(p2)
    fifo.enqueue(p3)
    fifo.display()

    pri = PriorityQueue()
    pri.enqueue(p1)
    pri.enqueue(p2)
    pri.enqueue(p3)
    pri.display()

def main():
    print("===== 机场登机口管理系统 Part1 工具箱 =====")
    # 1. 生成根目录CSV数据集
    generate_all_datasets()
    # 2. 加载数据
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    print(f"\n加载数据统计：")
    print(f"登机口总数：{len(gates)}")
    print(f"航班总数：{len(flights)}")
    print(f"乘客总数：{len(passengers)}")
    # 3. 初始化登机口网络图
    gate_graph = init_gate_graph()
    gate_graph.display_graph()
    # 4. 演示队列
    demo_queue_function()

if __name__ == "__main__":
    main()