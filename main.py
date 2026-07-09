# main.py 完整整合版
import sys
import os

# ====================== 全局路径初始化（放文件最顶部，解决导入报错） ======================
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入工具箱底层数据、队列、模型（你原有代码保留）
from toolbox.data_gen import generate_all_datasets, load_gates, load_flights, load_passengers, init_gate_graph, link_full_system, check_queue_coherence, generate_project_documents
from toolbox.queue import LinkedListQueue
from toolbox.models import Passenger

# ====================== 原有队列演示函数（完全保留） ======================
def demo_queue_function():
    """演示两种队列使用"""
    print("\n===== 队列功能演示（基于批量数据集） =====")

# ====================== 底层完整数据系统演示（原main函数逻辑） ======================
def run_full_data_demo():
    """完整运行数据集生成、加载、登机口图、队列校验全套流程"""
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

# ====================== Part2 三个子任务运行封装 ======================
def run_task5_gui():
    """Task5：延误级联可视化界面"""
    print("\n===== 启动Task5 延误级联可视化GUI =====")
    from part2.task5 import run_gui
    run_gui()

def run_task4_benchmark():
    """Task4：性能基准压力测试，生成三条性能曲线"""
    print("\n===== 启动Task4 性能基准测试 =====")
    from part2.task4 import run_full_benchmark
    run_full_benchmark()

def run_task2_boarding_sim():
    """Task2：登机仿真程序"""
    print("\n===== 启动Task2 登机仿真 =====")
    from part2.task2 import simulate_boarding
    simulate_boarding()

# ====================== 主菜单展示 ======================
def show_main_menu():
    print("\n==================== Airport Gate Manager 主菜单 ====================")
    print("1. 运行完整底层数据演示（生成CSV+登机口图+队列校验）")
    print("2. Task2：运行登机仿真程序")
    print("3. Task4：性能基准测试（生成三条性能曲线）")
    print("4. Task5：延误级联可视化图形界面")
    print("0. 退出程序")
    print("======================================================================")

# ====================== 程序总入口 ======================
if __name__ == "__main__":
    while True:
        show_main_menu()
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
            print("程序正常退出，再见！")
            break
        else:
            print("输入无效，请输入 0~4 之间数字！")