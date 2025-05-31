from model.instance import EVRPTWInstance
from model.solution import Solution
from common.utils import compute_route_distance

class ALNSState:
    def __init__(self, instance: EVRPTWInstance, routes: list[list[int]], unassigned: list[int] = None) -> None:
        self.instance = instance
        self.routes = routes
        self.unassigned = unassigned if unassigned else []

    def copy(self) -> 'ALNSState':
        return ALNSState(
            instance=self.instance,
            routes=[list(route) for route in self.routes],
            unassigned=self.unassigned.copy()
        )

    def objective(self) -> float:
        return sum(compute_route_distance(self.instance, route) for route in self.routes)

    @property
    def cost(self) -> float:
        return self.objective()

    def find_route(self, customer: int) -> list[int]:
        for route in self.routes:
            if customer in route:
                return route
        raise ValueError(f"Customer {customer} not in any route.")

    @classmethod
    def from_solution(cls, instance: EVRPTWInstance, solution: Solution) -> 'ALNSState':
        return cls(instance=instance, routes=[list(r) for r in solution.routes])
