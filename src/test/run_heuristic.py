from pathlib import Path
import time

from data import read_evrptw_instance, save_solution_to_file
from construction import construct_greedy_solution
from local_search import local_search
from alns_solve import run_alns
from .heuristic_mode import HeuristicMode

def run_heuristic_on_all_instances(instance_folder: str, solution_folder: str, mode: HeuristicMode) -> None:
    instance_folder = Path(instance_folder)
    solution_folder = Path(solution_folder)
    solution_folder.mkdir(parents=True, exist_ok=True)

    for instance_file in instance_folder.glob("*.txt"):
        instance_name = instance_file.stem
        print(f"\n=== Solving instance: {instance_name} ===")

        instance = read_evrptw_instance(instance_file)

        start_construct = time.time()
        initial_solution = construct_greedy_solution(instance)
        construct_time = time.time() - start_construct
        construct_distance = initial_solution.total_distance

        if mode == HeuristicMode.CONSTRUCT_ONLY:
            final_solution = initial_solution
            final_distance = construct_distance
            final_time = construct_time
        elif mode == HeuristicMode.CONSTRUCT_LOCAL:
            start_local = time.time()
            final_solution = local_search(instance, initial_solution)
            final_time = time.time() - start_local
            final_distance = final_solution.total_distance
        elif mode == HeuristicMode.CONSTRUCT_ALNS:
            start_alns = time.time()
            final_solution = run_alns(instance, initial_solution)
            final_time = time.time() - start_alns
            final_distance = final_solution.total_distance
        else:
            raise ValueError(f"Unknown mode: {mode}")

        save_solution_to_file(final_solution, instance, solution_folder, f"{instance_name}.sol")

        print(f"[RESULT] Construct → Distance: {construct_distance} | Time: {construct_time} sec")
        print(f"[RESULT] Final     → Distance: {final_distance} | Time: {final_time} sec")
