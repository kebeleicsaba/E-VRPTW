from pathlib import Path
import time

from data import read_evrptw_instance, save_solution_to_file
from construction import construct_greedy_solution
from local_search import local_search

def run_heuristic_on_all_instances(instance_folder: str, solution_folder: str) -> None:
    instance_folder = Path(instance_folder)
    solution_folder = Path(solution_folder)
    solution_folder.mkdir(parents=True, exist_ok=True)

    for instance_file in instance_folder.glob("*.txt"):
        instance_name = instance_file.stem
        print(f"\n=== Solving instance: {instance_name} ===")

        instance = read_evrptw_instance(instance_file)

        # --- Construct phase ---
        start_construct = time.time()
        initial_solution = construct_greedy_solution(instance)
        construct_time = time.time() - start_construct
        construct_distance = initial_solution.total_distance

        # --- Local search phase ---
        start_local = time.time()
        improved_solution = local_search(instance, initial_solution)
        local_time = time.time() - start_local
        local_distance = improved_solution.total_distance

        save_solution_to_file(improved_solution, instance, solution_folder, f"{instance_name}.sol")

        # --- Output summary ---
        print(f"[RESULT] Construct   → Distance: {construct_distance:.2f} | Time: {construct_time:.2f} sec")
        print(f"[RESULT] LocalSearch → Distance: {local_distance:.2f} | Time: {local_time:.2f} sec")

