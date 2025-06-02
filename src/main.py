from pathlib import Path
from test import (
    run_verifier_all_solutions_in_directories,
    run_heuristic_on_all_instances,
    tune_wait_time_weight_on_folder,
    multi_seed_alns_experiment,
    HeuristicMode
)

if __name__ == "__main__":
    verifier_path = Path("../pyEVRPVerifier/src/main.py")
    instance_folder = Path("../instances/instances")
    solution_folder = Path("../solutions/local_search")
    log_folder = Path("../logs")

    #construction_config_path = Path("./config/construction_config.json")
    #weight_values = [round(x * 0.025, 3) for x in range(0, int(1 / 0.025) + 1)]
    #tune_wait_time_weight_on_folder(instance_folder, solution_folder, construction_config_path, weight_values)

    #run_heuristic_on_all_instances(
    #    instance_folder=instance_folder,
    #    solution_folder=solution_folder,
    #    mode=HeuristicMode.CONSTRUCT_LOCAL,
    #    log_folder=log_folder
    #)

    seed_values = [1234, 5678, 42, 10001, 4321]
    multi_seed_alns_experiment(
        instance_folder="../instances/instances",
        base_solution_folder="../solutions/alns",
        base_log_folder="../logs/alns",
        base_config_path="./config/alns_config.json",
        seed_values=seed_values,
        mode=HeuristicMode.CONSTRUCT_ALNS
    )

    #run_verifier_all_solutions_in_directories(verifier_path, instance_folder, solution_folder)
