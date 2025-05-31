from pathlib import Path
from model.instance import EVRPTWInstance
from model.solution import Solution

def save_solution_to_file(solution: Solution, instance: EVRPTWInstance, output_dir: str, filename: str):
    """Saves the given solution to a file in the specified directory."""
    route_lines = []
    for route in solution.routes:
        node_names = [instance.nodes[i].string_id for i in route]
        route_lines.append(", ".join(node_names))

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(output_dir) / filename

    with open(file_path, "w") as f:
        f.write(f"{solution.total_distance}\n")
        for route in route_lines:
            f.write(route + "\n")
