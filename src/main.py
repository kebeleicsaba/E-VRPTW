from test import run_verifier_all_solutions_in_directories, run_heuristic_on_all_instances, tune_wait_time_weight_on_folder, HeuristicMode

if __name__ == "__main__":
    verifier_path = "../pyEVRPVerifier/src/main.py"
    instance_folder = "../instances/instances"
    solution_folder = "../solutions/construction"

    #construction_config_path = "./config/construction_config.json"
    #weight_values = [round(x * 0.025, 3) for x in range(0, int(1 / 0.025) + 1)]
    #tune_wait_time_weight_on_folder(instance_folder, solution_folder, construction_config_path, weight_values)

    solution_folder = "../solutions/alns"
    run_heuristic_on_all_instances(instance_folder, solution_folder, mode=HeuristicMode.CONSTRUCT_ALNS)
    run_verifier_all_solutions_in_directories(verifier_path, instance_folder, solution_folder)