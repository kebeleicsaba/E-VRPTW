import json
from pathlib import Path

from .run_heuristic import run_heuristic_on_all_instances

def multi_seed_alns_experiment(instance_folder, base_solution_folder, base_log_folder, base_config_path, seed_values, mode):
    instance_folder = Path(instance_folder)
    base_solution_folder = Path(base_solution_folder)
    base_log_folder = Path(base_log_folder)
    base_config_path = Path(base_config_path)

    with open(base_config_path) as f:
        base_config = json.load(f)

    for seed in seed_values:
        config = base_config.copy()
        config['seed'] = seed
        with open(base_config_path, "w") as f:
            json.dump(config, f, indent=2)

        solution_folder = base_solution_folder.parent / f"{base_solution_folder.name}_seed{seed}"
        log_folder = base_log_folder.parent / f"{base_log_folder.name}_seed{seed}"

        print(f"\n=== Running all instances with seed {seed} ===")
        run_heuristic_on_all_instances(
            instance_folder=str(instance_folder),
            solution_folder=str(solution_folder),
            mode=mode,
            log_folder=str(log_folder)
        )

    print("\n=== ALL SEEDS READY ===")
