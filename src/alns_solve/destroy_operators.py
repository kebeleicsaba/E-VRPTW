from .alns_state import ALNSState
from model.instance import EVRPTWInstance
from common.utils import compute_route_distance

def random_customer_removal(state: ALNSState, rnd, **kwargs) -> ALNSState:
    """Randomly removes a fraction of customers from the solution."""
    xi = kwargs.get("xi", 0.2)
    destroyed = state.copy()

    customers = [
        customer
        for route in destroyed.routes
        for customer in route
        if customer in destroyed.instance.customer_ids
    ]

    if not customers:
        return destroyed

    max_to_remove = max(1, int(len(customers) * xi))
    num_to_remove = rnd.integers(1, max_to_remove + 1)
    to_remove = rnd.choice(customers, size=num_to_remove, replace=False).tolist()

    for customer in to_remove:
        route = destroyed.find_route(customer)
        route.remove(customer)
        destroyed.unassigned.append(customer)

    destroyed.routes = [r for r in destroyed.routes if r]
    return destroyed

def nearest_customers_removal(state: ALNSState, rnd, **kwargs) -> ALNSState:
    """Removes a randomly selected customer and its nearest neighbors based on distance."""
    xi = kwargs.get("xi", 0.2)
    instance: EVRPTWInstance = state.instance
    destroyed = state.copy()

    customer_nodes = instance.customer_ids

    central_customer = rnd.choice(customer_nodes)

    others = [n for n in customer_nodes if n != central_customer]
    others.sort(key=lambda n: instance.distance(central_customer, n))

    max_to_remove = max(1, int(len(customer_nodes) * xi))
    num_to_remove = rnd.integers(1, max_to_remove + 1)

    to_remove = [central_customer] + others[:num_to_remove - 1]

    for node in to_remove:
        removed = False
        for _, route in enumerate(destroyed.routes):
            if node in route:
                route.remove(node)
                destroyed.unassigned.append(node)
                removed = True
                break
        if not removed:
            print(f"[WARNING] Customer {node} was not found in any route")

    destroyed.routes = [r for r in destroyed.routes if len(r) > 2]
    return destroyed

def worst_customer_removal(state: ALNSState, rnd, **kwargs) -> ALNSState:
    """Removes the worst customers based on removal gain."""
    xi = kwargs.get("xi", 0.2)
    p = kwargs.get("p", 10)
    destroyed = state.copy()
    instance: EVRPTWInstance = destroyed.instance

    removable_customers = []
    for route_idx, route in enumerate(destroyed.routes):
        for i in range(1, len(route) - 1):
            customer = route[i]
            if not instance.is_customer(customer):
                continue

            gain = calculate_removal_gain(instance, route, i)
            removable_customers.append((gain, route_idx, customer))

    if not removable_customers:
        return destroyed

    removable_customers.sort(reverse=True)
    max_to_remove = max(1, int(len(removable_customers) * xi))
    num_to_remove = rnd.integers(1, max_to_remove + 1)

    removed_customers = set()

    for _ in range(num_to_remove):
        if not removable_customers:
            break

        index = int(rnd.random() ** p * len(removable_customers))
        _, route_idx, customer = removable_customers.pop(index)

        if customer in removed_customers:
            continue

        route = destroyed.routes[route_idx]
        try:
            customer_index = route.index(customer)
            route.pop(customer_index)
            destroyed.unassigned.append(customer)
            removed_customers.add(customer)
        except ValueError:
            continue

    destroyed.routes = [r for r in destroyed.routes if len(r) > 2]
    return destroyed

def worst_station_removal(state: ALNSState, rnd, **kwargs) -> ALNSState:
    xi = kwargs.get("xi", 0.2)
    p = kwargs.get("p", 6)
    destroyed = state.copy()
    instance: EVRPTWInstance = destroyed.instance

    num_to_remove = rnd.integers(1, max(1, int(len(destroyed.routes)) * xi) + 1)
    removed_stations = set()

    for _ in range(num_to_remove):
        removable_stations = get_removable_stations(instance, destroyed.routes)
        if not removable_stations:
            break

        removable_stations.sort(reverse=True)
        index = int(rnd.random() ** p * len(removable_stations))
        _, route_idx, station_index, station = removable_stations.pop(index)

        if station in removed_stations:
            continue

        route = destroyed.routes[route_idx]

        # Find start of the segment
        start_index = station_index - 1
        while start_index >= 0:
            if instance.is_station(route[start_index]) or instance.is_depot(route[start_index]):
                break
            start_index -= 1
        start_index = max(0, start_index + 1)

        # Find end of the segment
        end_index = station_index + 1
        while end_index < len(route):
            if instance.is_station(route[end_index]) or instance.is_depot(route[end_index]):
                break
            end_index += 1
        end_index = min(len(route) - 1, end_index - 1)

        # Remove station
        route.pop(station_index)
        removed_stations.add(station)

        # Adjust end index if it shifted due to pop
        if station_index < end_index:
            end_index -= 1

        remove_customers_until_energy_feasible(
            instance,
            route,
            start_index,
            end_index,
            destroyed.unassigned,
        )

        # Final energy check
        #if not check_energy_feasibility(instance, route):
        #    print(f"[ERROR] Route {route_idx} infeasible even after removals: {route}")

    destroyed.routes = [r for r in destroyed.routes if len(r) > 2]
    return destroyed

def get_removable_stations(instance: EVRPTWInstance, routes: list[list[int]]) -> list[tuple[float, int, int, int]]:
    """Get all removable stations from the routes with their gain."""
    removable_stations = []

    for route_idx, route in enumerate(routes):
        for i in range(1, len(route) - 1):
            node = route[i]
            if not instance.is_station(node):
                continue

            new_route = route[:i] + route[i + 1:]
            old_cost = compute_route_distance(instance, route)
            new_cost = compute_route_distance(instance, new_route)
            gain = old_cost - new_cost

            removable_stations.append((gain, route_idx, i, node))

    return removable_stations

def remove_customers_until_energy_feasible(instance: EVRPTWInstance, route: list[int], start_index: int, end_index: int, unassigned: list[int]) -> None:
    """Remove customers from a certain segment of the route until it becomes energy feasible."""
    while not check_energy_feasibility(instance, route):
        removed = False

        for i in range(end_index, start_index - 1, -1):
            node = route[i]
            if instance.is_customer(node):
                unassigned.append(node)
                route.pop(i)
                end_index = min(end_index, len(route) - 1)
                removed = True
                break

        if removed:
            continue

        for i in range(start_index, min(end_index + 1, len(route))):
            node = route[i]
            if instance.is_customer(node):
                unassigned.append(node)
                route.pop(i)
                end_index = min(end_index, len(route) - 1)
                removed = True
                break

        if not removed:
            break

def check_energy_feasibility(instance: EVRPTWInstance, route: list[int]) -> bool:
    """Check if the given route is feasible in terms of energy consumption."""
    soc = instance.vehicle_energy_capacity
    last_node = route[0]

    for node in route[1:]:
        energy_used = instance.energy_consumption(last_node, node)

        if soc - energy_used < 0:
            return False

        if instance.is_station(node):
            soc = instance.vehicle_energy_capacity
        else:
            soc -= energy_used

        last_node = node

    return True

def calculate_removal_gain(instance, route: list[int], position: int) -> float:
    """Calculate the gain of removing a node from a route."""
    prev_node = route[position - 1]
    node = route[position]
    next_node = route[position + 1]

    cost_with_node = instance.distance(prev_node, node) + instance.distance(node, next_node)
    cost_without_node = instance.distance(prev_node, next_node)

    return cost_with_node - cost_without_node