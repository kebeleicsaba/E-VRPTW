from pathlib import Path
import json

from alns import ALNS
from alns.accept import SimulatedAnnealing
from alns.select import RandomSelect
from alns.stop import MaxIterations

from model.instance import EVRPTWInstance
from model.solution import Solution
from .alns_state import ALNSState
from .destroy_operators import dummy_destroy
from .repair_operators import dummy_repair

def run_alns(instance: EVRPTWInstance, initial_solution: Solution) -> Solution:
    config_path = Path(__file__).parent.parent / "config" / "alns_config.json"
    with open(config_path) as f:
        config = json.load(f)

    alns = ALNS()

    alns.add_destroy_operator(dummy_destroy)
    alns.add_repair_operator(dummy_repair)

    num_iterations = config["num_iterations"]

    initial_state = ALNSState.from_solution(instance, initial_solution)
    selector = RandomSelect(len(alns.destroy_operators), len(alns.repair_operators))
    criterion = SimulatedAnnealing(
        start_temperature=config["simulated_annealing"]["start_temperature"],
        end_temperature=config["simulated_annealing"]["end_temperature"],
        step=1 - config["simulated_annealing"]["step"],
        method=config["simulated_annealing"]["method"]
    )
    stop = MaxIterations(num_iterations)

    result = alns.iterate(
        initial_solution=initial_state,
        op_select=selector,
        accept=criterion,
        stop=stop,
        objective=lambda state: state.cost,
    )

    best_state: ALNSState = result.best_state
    best_solution = Solution(routes=best_state.routes)
    best_solution.compute_total_distance(instance)
    return best_solution
