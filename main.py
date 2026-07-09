# 新增路径适配代码，原有逻辑全部保留
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from toolbox.data_gen import generate_all_datasets, load_gates, load_flights, load_passengers, init_gate_graph, link_full_system, check_queue_coherence, generate_project_documents
from toolbox.queue import LinkedListQueue
from toolbox.models import Passenger

def demo_queue_function():
    """演示两种队列使用"""
    print("\n===== 队列功能演示（基于批量数据集） =====")

def main():
    print("===== 机场登机口管理系统 Part2 一体化完整系统 =====")
    generate_project_documents()
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
    print("\n===== 机场登机口拓扑图 =====")
    gate_graph.display_graph()
    # 四层全链路绑定
    link_full_system(gates, flights, passengers)

    print("\n======== 单航班登机队列演示（CSV数据集真实乘客，自动同步优先堆） ========")
    single_flight = list(flights.values())[0]
    print(f"\n--- {single_flight} ---")
    single_flight.gate.boarding_queue.display_all()

    sync_result = check_queue_coherence(single_flight.gate.boarding_queue)
    print(f"FIFO与优先堆数据一致性校验: {'通过' if sync_result else '不一致'}")

    print("> 执行一次出队操作：")
    removed_pax = single_flight.gate.boarding_queue.dequeue()
    print(f"移出旅客: {removed_pax}")
    single_flight.gate.boarding_queue.display_all()

    sync_after_dequeue = check_queue_coherence(single_flight.gate.boarding_queue)
    print(f"出队后一致性校验: {'通过' if sync_after_dequeue else '不一致'}")

    demo_queue_function()

if __name__ == "__main__":
    main()