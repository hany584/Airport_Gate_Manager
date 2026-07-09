# main.py
import sys
import os

# 全局路径初始化，放在文件最顶部
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 保留你原有全部工具箱导入
from toolbox.data_gen import generate_all_datasets, load_gates, load_flights, load_passengers, init_gate_graph, link_full_system, check_queue_coherence, generate_project_documents
from toolbox.queue import LinkedListQueue
from toolbox.models import Passenger

# 原有队列演示函数完全保留
def demo_queue_function():
    """演示两种队列使用"""
    print("\n===== 队列功能演示（基于批量数据集） =====")

# 原有完整底层数据演示逻辑（CSV生成、加载、拓扑图、队列校验全部保留）
def run_full_data_demo():
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
    # 四层全链路绑定【关键】乘客-航班-登机口关联
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
    return gates, flights, passengers

# Part2 Task2 登机仿真【修复：加载数据后执行link_full_system绑定对象关系】
def run_task2_boarding_sim():
    """Task2 登机仿真，自动生成、加载、绑定数据再运行仿真"""
    print("\n===== 启动Task2 登机仿真 =====")
    from part2.task2 import simulate_boarding
    # 1. 生成CSV
    generate_all_datasets()
    # 2. 加载三类数据
    gates = load_gates()
    flights = load_flights()
    passengers = load_passengers()
    # 3. 核心修复：绑定乘客-航班-登机口关联，p.flight不再是None
    link_full_system(gates, flights, passengers)
    # 4. 传入完整关联好的数据运行仿真
    missed = simulate_boarding(gates, flights, passengers)
    print(f"登机仿真运行完成！本次错过中转乘客总数：{missed}")

# Part2 Task4 性能基准测试，生成三条性能曲线
def run_task4_benchmark():
    print("\n===== 启动Task4 性能基准测试 =====")
    from part2.task4 import run_full_benchmark
    run_full_benchmark()

# Part2 Task5 可视化修复：不导入run_gui，直接运行文件
def run_task5_gui():
    print("\n===== 启动Task5 延误级联可视化界面 =====")
    import part2.task5

# 程序主入口，菜单内嵌循环，无独立show_main_menu函数
if __name__ == "__main__":
    while True:
        print("\n==================== Airport Gate Manager ====================")
        print("1. 运行完整底层数据演示（生成CSV、登机口拓扑、队列校验）")
        print("2. 运行 Part2 Task2 登机仿真")
        print("3. 运行 Part2 Task4 性能基准测试（生成三条耗时曲线）")
        print("4. 运行 Part2 Task5 延误级联可视化动画界面")
        print("0. 退出程序")
        print("==============================================================")
        user_choice = input("请输入功能序号：").strip()

        if user_choice == "1":
            run_full_data_demo()
        elif user_choice == "2":
            run_task2_boarding_sim()
        elif user_choice == "3":
            run_task4_benchmark()
        elif user_choice == "4":
            run_task5_gui()
        elif user_choice == "0":
            print("程序正常退出")
            break
        else:
            print("输入无效，请输入0-4之间数字！")