from .alns_state import ALNSState
from common.utils import check_route_feasibility_constraints, find_best_station_for_customer_insert, compute_route_distance
from model.instance import EVRPTWInstance

def greedy_repair(state: ALNSState, rnd, **kwargs) -> ALNSState:
    """Greedy repair operator that inserts unassigned customers into the best feasible positions (with a bit of randomness)."""
    repaired = state.copy()
    instance = repaired.instance
    p = kwargs.get("p", 10)

    insertion_cache = {
        customer: get_all_feasible_insertion_options(instance, repaired, customer)
        for customer in repaired.unassigned
    }

    while repaired.unassigned:
        best_customer = None
        best_option = None
        best_cost = float("inf")

        for customer, options in insertion_cache.items():
            if not options:
                continue
            options.sort()
            index = int(rnd.random() ** p * len(options))
            cost, route_idx, updated_route = options[index]

            if cost < best_cost:
                best_cost = cost
                best_customer = customer
                best_option = (cost, route_idx, updated_route)

        if best_customer is None:
            print("[WARNING] No feasible insertions found for remaining customers.")
            break

        _, route_idx, updated_route = best_option
        if route_idx == len(repaired.routes):
            repaired.routes.append(updated_route)
        else:
            repaired.routes[route_idx] = updated_route
        repaired.unassigned.remove(best_customer)

        affected_customers = [
            customer for customer in repaired.unassigned
            if any(route_idx == idx for _, idx, _ in insertion_cache.get(customer, []))
        ]
        for customer in affected_customers:
            insertion_cache[customer] = get_all_feasible_insertion_options(instance, repaired, customer)

        insertion_cache.pop(best_customer, None)

    return repaired

def regret_repair(state: ALNSState, rnd, **kwargs) -> ALNSState:
    """Regret-based repair operator that selects the customer with the highest regret for insertion. (with a bit of randomness)"""
    repaired = state.copy()
    instance = repaired.instance
    p = kwargs.get("p", 10)

    insertion_cache = {
        customer: get_all_feasible_insertion_options(instance, repaired, customer)
        for customer in repaired.unassigned
    }

    while repaired.unassigned:
        regret_list = []

        for customer, options in insertion_cache.items():
            if len(options) < 1:
                continue

            options.sort()
            if len(options) == 1:
                regret = 0
                best_option = options[0]
            else:
                regret = options[1][0] - options[0][0]
                best_option = options[0]

            regret_list.append((regret, customer, best_option))

        if not regret_list:
            print("[WARNING] No feasible insertions found for remaining customers.")
            break

        regret_list.sort(reverse=True)
        index = int(rnd.random() ** p * len(regret_list))
        _, selected_customer, (_, route_idx, updated_route) = regret_list[index]

        if route_idx == len(repaired.routes):
            repaired.routes.append(updated_route)
        else:
            repaired.routes[route_idx] = updated_route
        repaired.unassigned.remove(selected_customer)

        affected_customers = [
            customer for customer in repaired.unassigned
            if any(route_idx == idx for _, idx, _ in insertion_cache.get(customer, []))
        ]
        for customer in affected_customers:
            insertion_cache[customer] = get_all_feasible_insertion_options(instance, repaired, customer)

        insertion_cache.pop(selected_customer, None)

    return repaired

def get_all_feasible_insertion_options(instance: EVRPTWInstance, repaired: ALNSState, customer: int) -> list[tuple[float, int, list[int]]]:
    """Finds all feasible insertion options for a customer"""
    insertion_options = []

    fallback_needed = True

    for route_idx, route in enumerate(repaired.routes):
        for pos in range(1, len(route)):
            new_route = route[:pos] + [customer] + route[pos:]
            time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, new_route)

            if time_ok and cap_ok and energy_ok: # Direct insertion without station
                cost = (
                    instance.distance(route[pos - 1], customer)
                    + instance.distance(customer, route[pos])
                    - instance.distance(route[pos - 1], route[pos])
                )
                insertion_options.append((cost, route_idx, new_route))
                fallback_needed = False
            elif time_ok and cap_ok:
                for before in [True, False]: # [..., station, customer, ...] or [..., customer, station, ...]
                    updated_route = find_best_station_for_customer_insert(instance, route, customer, pos, before=before)
                    if updated_route:
                        cost = compute_route_distance(instance, updated_route) - compute_route_distance(instance, route)
                        insertion_options.append((cost, route_idx, updated_route))
                        fallback_needed = False

    # Try to insert a new vehicle 
    depot = instance.depot_id
    base_route = [depot, customer, depot]
    time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, base_route)

    if time_ok and cap_ok and energy_ok:
        cost = compute_route_distance(instance, base_route)
        insertion_options.append((cost, len(repaired.routes), base_route))
        fallback_needed = False
    elif time_ok and cap_ok:
        for before in [True, False]: # [depot, station, customer, depot] or [depot, customer, station, depot]
            route_with_station = find_best_station_for_customer_insert(instance, [depot, depot], customer, 1, before=before)
            if route_with_station:
                cost = compute_route_distance(instance, route_with_station)
                insertion_options.append((cost, len(repaired.routes), route_with_station))
                fallback_needed = False

    if fallback_needed: # [depot, station, customer, station, depot]
        for station1 in instance.station_ids:
            for station2 in instance.station_ids:
                fallback_route = [depot, station1, customer, station2, depot]
                time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, fallback_route)
                if time_ok and cap_ok and energy_ok:
                    cost = compute_route_distance(instance, fallback_route)
                    insertion_options.append((cost, len(repaired.routes), fallback_route))

    return insertion_options
