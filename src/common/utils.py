from model.instance import EVRPTWInstance

def compute_route_distance(instance: EVRPTWInstance, route: list[int]) -> float:
    """Returns the total distance of a single route."""
    return sum(
        instance.distance(route[i], route[i + 1])
        for i in range(len(route) - 1)
    )
