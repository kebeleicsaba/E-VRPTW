import os
import subprocess

def run_verifier_on_all_solutions(verifier_path: str, instance_folder: str, solution_folder: str):
    for filename in os.listdir(instance_folder):
        if filename.endswith(".txt"):
            instance_path = os.path.join(instance_folder, filename)
            solution_name = os.path.splitext(filename)[0] + ".sol"
            solution_path = os.path.join(solution_folder, solution_name)

            if not os.path.exists(solution_path):
                print(f"❌ Megfelelő megoldás nem található: {solution_path}")
                continue

            command = [
                "python",
                verifier_path,
                "--instance", instance_path,
                "--solution", solution_path
            ]

            print(f"✔ Verifying {filename} with {solution_name}")
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Verifier failed on {filename}: {e}")

if __name__ == "__main__":
    verifier_path = "pyEVRPVerifier/src/main.py"
    instance_folder = "instances/instances"
    solution_folder = "solutions/local_search"

    run_verifier_on_all_solutions(verifier_path, instance_folder, solution_folder)
