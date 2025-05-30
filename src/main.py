from pathlib import Path

from data import read_evrptw_instance
from construction import construct_greedy_solution

def run_heuristic_on_all_instances(heuristic_fn, instance_folder: str, solution_folder: str) -> None:
    instance_folder = Path(instance_folder)
    solution_folder = Path(solution_folder)
    solution_folder.mkdir(parents=True, exist_ok=True)

    for instance_file in instance_folder.glob("*.txt"):
        instance_name = instance_file.stem 

        instance = read_evrptw_instance(instance_file)
        solution, run_time = heuristic_fn(instance)

        output_file = solution_folder / f"{instance_name}.sol"
        solution.save_solution(instance, solution_folder, output_file.name)

        #solution.pretty_print(instance)
        print(f"Saved solution to {output_file}")
        print(f"Run time: {run_time}")

if __name__ == "__main__":
    instance_folder = "../instances/instances"
    solution_folder = "../solutions"
    run_heuristic_on_all_instances(construct_greedy_solution, instance_folder, solution_folder)

#if __name__ == "__main__":
#    instance_folder = "instances"
#    instance_name = "rc106_21"
#    instance = read_evrptw_instance(f"../instances/{instance_folder}/{instance_name}.txt")
#    print(instance)
#    solution, time = construct_greedy_solution(instance)
#    solution.save_solution(instance, "../solutions", f"{instance_name}.sol")
#    solution.pretty_print(instance)
#    print(f"Constructed solution: {solution}")
