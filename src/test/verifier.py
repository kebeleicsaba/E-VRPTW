from pathlib import Path
import subprocess

def run_verifier_all_solutions_in_directories(verifier_path: str, instance_folder: str, solution_folder: str):
    """Runs the verifier script on all instance-solution file pairs in the given folders."""
    instance_dir = Path(instance_folder)
    solution_dir = Path(solution_folder)

    for instance_file in instance_dir.glob("*.txt"):
        solution_file = solution_dir / (instance_file.stem + ".sol")

        if not solution_file.exists():
            print(f"No solution found for: {solution_file}")
            continue

        command = [
            "python",
            verifier_path,
            "--instance", str(instance_file),
            "--solution", str(solution_file)
        ]

        print(f"✔ Verifying {instance_file.name} with {solution_file.name}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Verifier failed on {instance_file.name}: {e}")

def run_verifier_on_single_solution(verifier_path: str, instance_path: str, solution_path: str):
    """Runs the verifier script on a single instance and solution file."""
    instance_file = Path(instance_path)
    solution_file = Path(solution_path)

    if not solution_file.exists():
        print(f"Solution file does not exist: {solution_file}")
        return

    if not instance_file.exists():
        print(f"Instance file does not exist: {instance_file}")
        return

    command = [
        "python",
        verifier_path,
        "--instance", str(instance_file),
        "--solution", str(solution_file)
    ]

    print(f"✔ Verifying {instance_file.name} with {solution_file.name}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Verifier failed on {instance_file.name}: {e}")
