from model import EVRPTWInstance, Solution
from .relocate_descent import relocate_descent

def local_search(instance: EVRPTWInstance, initial_solution: Solution) -> Solution:
    """Runs a local search starting from the initial solution using Relocate descent."""
    print("\n[DEBUG] Starting local search with Relocate descent")
    current_solution = initial_solution.copy()
    improved = True
    iteration = 0

    while improved:
        iteration += 1
        print(f"[DEBUG] Iteration {iteration}")
        prev_distance = current_solution.total_distance
        improved, new_solution = relocate_descent(instance, current_solution)
        new_distance = new_solution.total_distance
        print(f"[DEBUG] Improved: {improved}, Previous distance: {prev_distance:.2f}, New distance: {new_distance:.2f}")
        if improved:
            current_solution = new_solution

    print(f"\n[DEBUG] Local search finished after {iteration} iteration(s)")
    return current_solution
