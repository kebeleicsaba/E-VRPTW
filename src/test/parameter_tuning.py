import json
from pathlib import Path
from collections import Counter
import csv

from construction import construct_greedy_solution
from data import read_evrptw_instance, save_solution_to_file

def tune_wait_time_weight_on_folder(instance_folder: str, solution_folder: str, config_path: str, weight_values):
    instance_folder = Path(instance_folder)
    config_path = Path(config_path)
    results = []

    for instance_file in sorted(instance_folder.glob("*.txt")):
        instance_name = instance_file.stem
        print(f"\nTuning instance: {instance_name}")
        instance = read_evrptw_instance(instance_file)

        best_weight = None
        best_distance = float("inf")
        best_solution = None
        distances = {}

        for w in weight_values:
            with open(config_path, 'w') as f:
                json.dump({"wait_time_weight": w}, f)

            solution = construct_greedy_solution(instance)
            if solution is None:
                print(f"Weight {w}: NO FEASIBLE SOLUTION")
                continue
            distance = solution.total_distance
            distances[w] = distance
            print(f"Weight {w}: Distance = {distance:.3f}")

            if distance < best_distance:
                best_distance = distance
                best_weight = w
                best_solution = solution

        results.append({
            "instance": instance_name,
            "best_weight": best_weight,
            "best_distance": best_distance,
            "all_distances": distances
        })

        if best_solution is not None:
            save_solution_to_file(
                best_solution, instance, solution_folder, f"{instance_name}.sol"
            )
        else:
            print(f"  {instance_name}: NO FEASIBLE SOLUTION for any weight.")

    best_weights = [r["best_weight"] for r in results if r["best_weight"] is not None]
    print("\nTuning summary:")
    print("Best weights distribution:", Counter(best_weights))
    print("Instance best weights/distances:")
    for r in results:
        print(f"  {r['instance']}: weight={r['best_weight']}  distance={r['best_distance']:.3f}")

    with open(Path(__file__).parent.parent.parent / "tables" / "construction_tune_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "best_weight", "best_distance"] + [f"dist_w={w}" for w in weight_values])
        for r in results:
            row = [r["instance"], r["best_weight"], r["best_distance"]]
            row += [r["all_distances"].get(w, "NA") for w in weight_values]
            writer.writerow(row)

    return results
    
