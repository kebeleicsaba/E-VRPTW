from model import EVRPTWInstance, Solution
from .relocate_descent import relocate_descent
import time

from data.log_saver import save_log
from model import EVRPTWInstance, Solution
from .relocate_descent import relocate_descent

def local_search(instance: EVRPTWInstance, initial_solution: Solution, log_path: str = None) -> Solution:
    """Runs a local search starting from the initial solution using Relocate descent."""
    #print("\n[DEBUG] Starting local search with Relocate descent")
    current_solution = initial_solution.copy()
    improved = True
    iteration = 0

    steps_log = []
    t0 = time.time()

    while improved:
        iteration += 1
        step_start = time.time()
        prev_distance = current_solution.total_distance
        improved, new_solution = relocate_descent(instance, current_solution)
        new_distance = new_solution.total_distance
        step_time = time.time() - step_start
        #print(f"[DEBUG] Improved: {improved}, Previous distance: {prev_distance:.2f}, New distance: {new_distance:.2f}")

        steps_log.append({
            "iteration": iteration,
            "improved": improved,
            "prev_distance": prev_distance,
            "new_distance": new_distance,
            "step_time": step_time,
        })

        if improved:
            current_solution = new_solution

    total_time = time.time() - t0
    #print(f"\n[DEBUG] Local search finished after {iteration} iteration(s)")

    if log_path:
        log_data = {
            "steps": steps_log,
            "total_iterations": iteration,
            "total_time": total_time,
            "final_solution": {
                "routes": current_solution.routes,
                "total_distance": current_solution.total_distance
            }
        }
        save_log(log_path, log_data)

    return current_solution

