from toolbox.data_gen import generate_all_datasets, load_gates, load_flights, load_passengers, init_gate_graph, link_full_system, check_queue_coherence, generate_project_documents
# 【MODIFIED 删除单独导入PriorityQueue，符合单向同步约束：仅通过FIFO内部获取堆，禁止独立实例化PriorityQueue】
from toolbox.queue import LinkedListQueue
from toolbox.models import Passenger




# NEW：新增批量数据集演示，匹配需求：主系统使用生成数据集展示队列
def demo_queue_function():
    """演示两种队列使用"""
    # 【MODIFIED 删除手动手写3个乘客，匹配需求：不用手写乘客，基于数据集演示】
    print("\n===== 队列功能演示（基于批量数据集） =====")


def main():
    print("===== 机场登机口管理系统 Part2 一体化完整系统 =====")
    # 【NEW 新增：启动自动生成requirements.txt + README.md，匹配需求Add a requirements.txt and a README】
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

    # 【NEW 新增全系统联动，匹配需求Link passengers with their flight and the flight with their gate, and the flight with the boarding queues.】
    # 完成 Passenger ↔ Flight ↔ Gate ↔ boarding_queue 四层全链路绑定
    link_full_system(gates, flights, passengers)

    # 【MODIFIED 数据集真实业务队列演示，区分手动测试乘客，满足需求：主系统使用生成数据集展示队列】
    print("\n======== 各航班登机队列演示（CSV数据集真实乘客，自动同步优先堆） ========")
    # 遍历前3个航班展示，避免输出过长
    for flight in list(flights.values())[:3]:
        print(f"\n--- {flight} ---")
        # 一键打印FIFO队列 + 自动同步的优先堆视图
        flight.gate.boarding_queue.display_all()
        # 校验FIFO与优先堆数据一致性，匹配测试需求FIFO and heap stay coherent
        sync_result = check_queue_coherence(flight.gate.boarding_queue)
        print(f"FIFO与优先堆数据一致性校验: {'✅ 通过' if sync_result else '❌ 不一致'}")

        # 演示出队操作，验证单向同步更新规则（仅修改FIFO自动同步堆，无反向调用）
        print("> 执行一次出队操作：")
        removed_pax = flight.gate.boarding_queue.dequeue()
        print(f"移出旅客: {removed_pax}")
        flight.gate.boarding_queue.display_all()
        sync_after_dequeue = check_queue_coherence(flight.gate.boarding_queue)
        print(f"出队后一致性校验: {'✅ 通过' if sync_after_dequeue else '❌ 不一致'}")

    # 调用基础手动测试队列演示
    demo_queue_function()


if __name__ == "__main__":
    main()