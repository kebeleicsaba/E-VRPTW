from typing import Optional

from model import EVRPTWInstance, Solution

def relocate_descent_without_station_change(instance: EVRPTWInstance, solution: Solution) -> tuple[bool, Solution]:
    """Tries to improve the solution using relocate moves, without adding stations."""
    best_solution = solution.copy()
    best_solution.compute_total_distance(instance)
    improved = False

    for i, route_i in enumerate(solution.routes):
        for j in range(len(route_i)):
            customer = route_i[j]
            if customer not in instance.customer_ids:
                continue # Skip if the node is depot or station

            for k, route_k in enumerate(solution.routes):
                if k == i:
                    continue 

                for pos in range(1, len(route_k)):
                    new_route_i = route_i[:j] + route_i[j+1:]
                    new_route_k = route_k[:pos] + [customer] + route_k[pos:]

                    time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, new_route_k)
                    if not (time_ok and cap_ok and energy_ok):
                        continue

                    temp_solution = solution.copy()
                    temp_solution.routes[i] = new_route_i
                    temp_solution.routes[k] = new_route_k
                    temp_solution.compute_total_distance(instance)

                    if temp_solution.total_distance < best_solution.total_distance:
                        improved = True
                        best_solution = temp_solution

    return improved, best_solution

def relocate_descent(instance: EVRPTWInstance, solution: Solution) -> tuple[bool, Solution]:
    """Tries to improve the solution using relocate moves."""
    best_solution = solution.copy()
    best_solution.compute_total_distance(instance)
    improved = False

    for i, route_i in enumerate(solution.routes):
        for j in range(len(route_i)):
            customer = route_i[j]
            if customer not in instance.customer_ids:
                continue

            for k, route_k in enumerate(solution.routes):
                if k == i:
                    continue

                for pos in range(1, len(route_k)):
                    new_route_i = route_i[:j] + route_i[j+1:]
                    new_route_k = route_k[:pos] + [customer] + route_k[pos:]

                    time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, new_route_k)
                    if not (time_ok and cap_ok):
                        continue

                    # CASE 1: Feasible without station
                    if energy_ok:
                        temp_solution = solution.copy()
                        temp_solution.routes[i] = new_route_i
                        temp_solution.routes[k] = new_route_k
                        temp_solution.compute_total_distance(instance)

                        if temp_solution.total_distance < best_solution.total_distance:
                            improved = True
                            best_solution = temp_solution
                        continue

                    # CASE 2: Try inserting station BEFORE customer
                    updated_route_k = find_best_station_for_customer_insert(instance, route_k, customer, pos, before=True)
                    if updated_route_k:
                        temp_solution = solution.copy()
                        temp_solution.routes[i] = new_route_i
                        temp_solution.routes[k] = updated_route_k
                        temp_solution.compute_total_distance(instance)

                        if temp_solution.total_distance < best_solution.total_distance:
                            improved = True
                            best_solution = temp_solution

                    # CASE 3: Try inserting station AFTER customer
                    updated_route_k = find_best_station_for_customer_insert(instance, route_k, customer, pos, before=False)
                    if updated_route_k:
                        temp_solution = solution.copy()
                        temp_solution.routes[i] = new_route_i
                        temp_solution.routes[k] = updated_route_k
                        temp_solution.compute_total_distance(instance)

                        if temp_solution.total_distance < best_solution.total_distance:
                            improved = True
                            best_solution = temp_solution

    return improved, best_solution

def check_route_feasibility_constraints(instance: EVRPTWInstance, route: list[int]) -> tuple[bool, bool, bool]:
    """
    Checks whether the given route satisfies all key feasibility constraints.
    Returns (time_feasible, capacity_feasible, energy_feasible) for the given route.
    """
    # Idea: We do not need to check the whole route, just from the inserted customer to the end. But we need to store the informations (only the remaining energy and the remaining capacity!?) about the previous part of the route
    capacity = instance.vehicle_load_capacity
    soc = instance.vehicle_energy_capacity  # State of charge
    time = 0.0
    last_node = route[0] 

    time_feasible = True
    capacity_feasible = True
    energy_feasible = True

    for node in route[1:]:
        demand = instance.demand(node) if node in instance.customer_ids else 0
        travel_time = instance.travel_time(last_node, node)
        energy_used = instance.energy_consumption(last_node, node)
        arrival_time = time + travel_time

        if soc - energy_used < 0:
            energy_feasible = False

        if node in instance.customer_ids:
            ready = instance.ready(node)
            due = instance.due(node)
            service_time = instance.service_time(node)
            start_service = max(arrival_time, ready)
            end_service = start_service + service_time

            if start_service > due:
                time_feasible = False

            if demand > capacity:
                capacity_feasible = False

            time = end_service
            capacity -= demand
            soc -= energy_used

        elif node in instance.station_ids:
            recharge_amount = instance.vehicle_energy_capacity - max(0.0, soc - energy_used)
            recharge_time = instance.time_for_recharging_energy(recharge_amount)
            time = arrival_time + recharge_time
            soc = instance.vehicle_energy_capacity  # full recharge

        else:  # depot
            time = arrival_time
            soc -= energy_used
            due = instance.due(node)
            if time > due:
                time_feasible = False

        last_node = node

    return time_feasible, capacity_feasible, energy_feasible

def find_best_station_for_customer_insert(instance: EVRPTWInstance, route: list[int], customer: int, insert_pos: int, before: bool) -> Optional[list[int]]:
    """Returns the best updated route with a station inserted before or after the customer, or None if no feasible route exists."""
    best_route = None
    best_distance = float('inf')

    for station_id in instance.station_ids:
        if before:
            candidate = route[:insert_pos] + [station_id, customer] + route[insert_pos:]
        else:
            candidate = route[:insert_pos] + [customer, station_id] + route[insert_pos:]

        time_ok, cap_ok, energy_ok = check_route_feasibility_constraints(instance, candidate)
        if not (time_ok and cap_ok and energy_ok):
            continue

        distance = compute_route_distance(instance, candidate)
        if distance < best_distance:
            best_distance = distance
            best_route = candidate

    return best_route

def compute_route_distance(instance: EVRPTWInstance, route: list[int]) -> float:
    """Returns the total distance of a single route."""
    total_distance = 0.0
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        total_distance += instance.distance(u, v)
    return total_distance