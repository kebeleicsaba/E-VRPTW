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
    alns = ALNS()

    num_iterations = 1000

    alns.add_destroy_operator(dummy_destroy)
    alns.add_repair_operator(dummy_repair)

    num_destroy = len(alns.destroy_operators)
    num_repair = len(alns.repair_operators)

    selector = RandomSelect(num_destroy, num_repair)
    stop = MaxIterations(num_iterations)

    initial_state = ALNSState.from_solution(instance, initial_solution)

    criterion = SimulatedAnnealing(
        start_temperature=1000,
        end_temperature=1,
        step=1 - 1e-3,
        method="exponential"
    )

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
