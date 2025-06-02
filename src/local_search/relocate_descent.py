from model import EVRPTWInstance, Solution
from common.utils import check_route_feasibility_constraints, find_best_station_for_customer_insert

def relocate_descent_without_station_change(instance: EVRPTWInstance, solution: Solution) -> tuple[bool, Solution]:
    """Tries to improve the solution using relocate moves, without adding stations."""
    best_solution = solution.copy()
    best_solution.compute_total_distance(instance)
    improved = False

    for i, route_i in enumerate(solution.routes):
        for j in range(len(route_i)):
            customer = route_i[j]
            if not instance.is_customer(customer):
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
            if not instance.is_customer(customer):
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

