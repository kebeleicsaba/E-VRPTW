from pathlib import Path
import time

from data import read_evrptw_instance, save_solution_to_file
from construction import construct_greedy_solution
from local_search import local_search
from alns_solve import run_alns
from .heuristic_mode import HeuristicMode

def run_heuristic_on_all_instances(instance_folder: str, solution_folder: str, mode: HeuristicMode, log_folder: str = None) -> None:
    instance_folder = Path(instance_folder)
    solution_folder = Path(solution_folder)
    solution_folder.mkdir(parents=True, exist_ok=True)

    if log_folder is not None:
        log_folder = Path(log_folder)
        log_folder.mkdir(parents=True, exist_ok=True)
        construction_log_folder = log_folder / "construction"
        local_log_folder = log_folder / "local_search"
        alns_log_folder = log_folder / "alns"
        construction_log_folder.mkdir(parents=True, exist_ok=True)
        local_log_folder.mkdir(parents=True, exist_ok=True)
        alns_log_folder.mkdir(parents=True, exist_ok=True)
    else:
        construction_log_folder = local_log_folder = alns_log_folder = None

    for instance_file in instance_folder.glob("*.txt"):
        instance_name = instance_file.stem
        print(f"\n=== Solving instance: {instance_name} ===")

        instance = read_evrptw_instance(instance_file)

        construct_log_path = construction_log_folder / f"{instance_name}_log.json" if construction_log_folder else None
        local_log_path = local_log_folder / f"{instance_name}_log.json" if local_log_folder else None
        alns_log_path = alns_log_folder / f"{instance_name}_log.json" if alns_log_folder else None

        start_construct = time.time()
        initial_solution = construct_greedy_solution(instance, log_path=construct_log_path)
        construct_time = time.time() - start_construct
        construct_distance = initial_solution.total_distance

        if mode == HeuristicMode.CONSTRUCT_ONLY:
            final_solution = initial_solution
            final_distance = construct_distance
            final_time = construct_time
        elif mode == HeuristicMode.CONSTRUCT_LOCAL:
            start_local = time.time()
            final_solution = local_search(instance, initial_solution, log_path=local_log_path)
            final_time = time.time() - start_local
            final_distance = final_solution.total_distance
        elif mode == HeuristicMode.CONSTRUCT_ALNS:
            start_alns = time.time()
            final_solution = run_alns(instance, initial_solution, log_path=alns_log_path)
            final_time = time.time() - start_alns
            final_distance = final_solution.total_distance
        else:
            raise ValueError(f"Unknown mode: {mode}")

        save_solution_to_file(final_solution, instance, solution_folder, f"{instance_name}.sol")

        print(f"[RESULT] Construct → Distance: {construct_distance} | Time: {construct_time} sec")
        print(f"[RESULT] Final     → Distance: {final_distance} | Time: {final_time} sec")
