from pathlib import Path
import json
import numpy.random as rnd
#import matplotlib.pyplot as plt

from alns import ALNS
from alns.accept import SimulatedAnnealing
from alns.select import SegmentedRouletteWheel
from alns.stop import MaxIterations

from data.log_saver import save_log
from model.instance import EVRPTWInstance
from model.solution import Solution
from .alns_state import ALNSState
from .destroy_operators import random_customer_removal, nearest_customers_removal, worst_customer_removal, worst_station_removal
from .repair_operators import greedy_repair, regret_repair

def run_alns(instance: EVRPTWInstance, initial_solution: Solution, log_path: str = None) -> Solution:
    """Runs the Adaptive Large Neighborhood Search algorithm """
    config_path = Path(__file__).parent.parent / "config" / "alns_config.json"
    with open(config_path) as f:
        config = json.load(f)

    alns = ALNS(rnd.default_rng(config["seed"]))

    alns.add_destroy_operator(random_customer_removal)
    alns.add_destroy_operator(nearest_customers_removal)
    alns.add_destroy_operator(worst_customer_removal)
    alns.add_destroy_operator(worst_station_removal)
    alns.add_repair_operator(greedy_repair)
    alns.add_repair_operator(regret_repair)

    num_iterations = config["num_iterations"]

    initial_state = ALNSState.from_solution(instance, initial_solution)
    sel_cfg = config["selector"]
    sa_cfg = config["simulated_annealing"]
    selector = SegmentedRouletteWheel(
        scores=sel_cfg["scores"],
        decay=sel_cfg["decay"],
        seg_length=sel_cfg["seg_length"],
        num_destroy=sel_cfg["num_destroy"],
        num_repair=sel_cfg["num_repair"]
    )
    criterion = SimulatedAnnealing(
        start_temperature=sa_cfg["start_temperature"],
        end_temperature=sa_cfg["end_temperature"],
        step=1 - sa_cfg["step"],
        method=sa_cfg["method"]
    )
    stop = MaxIterations(num_iterations)

    result = alns.iterate(
        initial_solution=initial_state,
        op_select=selector,
        accept=criterion,
        stop=stop,
        objective=lambda state: state.cost,
        xi=config["xi"],
        p=config["p"]
    )

    best_state: ALNSState = result.best_state
    best_solution = Solution(routes=best_state.routes)
    best_solution.compute_total_distance(instance)

    #result.plot_operator_counts()
    #plt.gcf().set_size_inches(14, 8)
    #plt.tight_layout()

    #plt.savefig("operator_counts_large.png", dpi=200)

    stats = result.statistics

    destroy_operator_names = list(stats.destroy_operator_counts.keys())
    destroy_operator_counts = [stats.destroy_operator_counts[name] for name in destroy_operator_names]
    destroy_operator_total_counts = [sum(stats.destroy_operator_counts[name]) for name in destroy_operator_names]

    repair_operator_names = list(stats.repair_operator_counts.keys())
    repair_operator_counts = [stats.repair_operator_counts[name] for name in repair_operator_names]
    repair_operator_total_counts = [sum(stats.repair_operator_counts[name]) for name in repair_operator_names]

    if log_path:
        log_data = {
            "objectives": list(stats.objectives),
            "destroy_operator_names": destroy_operator_names,
            "destroy_operator_outcome_counts": destroy_operator_counts,
            "destroy_operator_total_counts": destroy_operator_total_counts,
            "repair_operator_names": repair_operator_names,
            "repair_operator_outcome_counts": repair_operator_counts,
            "repair_operator_total_counts": repair_operator_total_counts,
            "operator_outcome_labels": ["best", "better", "accepted", "rejected"],
            "runtimes": list(stats.runtimes),
            "total_runtime": stats.total_runtime,
            "num_iterations": num_iterations,
            "best_solution": {
                "total_distance": best_solution.total_distance,
                "routes": best_solution.routes
            }
        }
        save_log(log_path, log_data)

    return best_solution
