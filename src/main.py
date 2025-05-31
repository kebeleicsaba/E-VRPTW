from test import run_verifier_all_solutions_in_directories, run_heuristic_on_all_instances

if __name__ == "__main__":
    verifier_path = "../pyEVRPVerifier/src/main.py"
    instance_folder = "../instances/instances"
    solution_folder = "../solutions/local_search"
    run_heuristic_on_all_instances(instance_folder, solution_folder)
    run_verifier_all_solutions_in_directories(verifier_path, instance_folder, solution_folder)

