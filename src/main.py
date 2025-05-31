from test import run_verifier_all_solutions_in_directories, run_heuristic_on_all_instances, HeuristicMode

if __name__ == "__main__":
    verifier_path = "../pyEVRPVerifier/src/main.py"
    instance_folder = "../instances/instances"
    solution_folder = "../solutions/alns"

    run_heuristic_on_all_instances(instance_folder, solution_folder, mode=HeuristicMode.CONSTRUCT_ALNS)
    run_verifier_all_solutions_in_directories(verifier_path, instance_folder, solution_folder)
