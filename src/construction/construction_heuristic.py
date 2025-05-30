import time
from typing import Optional

from .customer_select import select_next_customer
from model import EVRPTWInstance, Solution, RouteStatus

def construct_greedy_solution(instance: EVRPTWInstance) -> Solution:
    """Constructs a greedy solution for the EVRPTW problem.
    The heuristic run until all customers are served or no feasible solution can be found.
    Each iteration constructs a route. 
    """
    start_time = time.time()
    routes = []
    unserved_customers = set(instance.customer_ids)

    while unserved_customers:
        route_status = initialize_route(instance)
        initial_unserved_count = len(unserved_customers)

        while True: # One route building iteration
            feasible_map = get_feasible_customers(instance, route_status, unserved_customers)
            if not feasible_map: # We cannot serve any customers directly, we have to try some recharging
                if not handle_no_feasible_customers(instance, route_status):
                    break # We cannot continue this route, we have to finish it
                continue # We can serve customers with recharging

            next_customer = select_next_customer(instance, route_status, list(feasible_map.keys()))
            if next_customer is None:
                break # No more customers can be selected, finish the route

            station_before = feasible_map[next_customer] 
            if station_before is not None: # If we need to visit a station before the customer
                update_route_status(instance, route_status, station_before, is_customer=False)

                arrival_time = route_status.last_service_end_time + instance.travel_time(route_status.current_location, next_customer)
                if arrival_time > instance.due(next_customer):
                    break # We cannot serve this customer after the station, because the arrival time changes -> Finish the route

            update_route_status(instance, route_status, next_customer, is_customer=True)
            unserved_customers.remove(next_customer)

        if len(unserved_customers) == initial_unserved_count: 
            print("No feasible solution could be found for remaining customers.")
            return None, time.time() - start_time # Infeasible solution, we cannot serve all customers

        if not finish_route(route_status, instance):
            print("Could not finish route properly.")
            return None, time.time() - start_time # Infeasible solution, we cannot return to depot

        routes.append(route_status)

    solution = Solution(routes=[r.route for r in routes])
    solution.compute_total_distance(instance)
    return solution, time.time() - start_time

def initialize_route(instance: EVRPTWInstance) -> RouteStatus:
    """Initializes a new route status for the given instance."""
    return RouteStatus(
        current_location=instance.depot_id,
        remaining_capacity=instance.vehicle_load_capacity,
        remaining_energy=instance.vehicle_energy_capacity,
        arrival_time=0.0,
        last_service_end_time=0.0,
        route=[instance.depot_id],
        total_distance=0.0
    )

def update_route_status(instance: EVRPTWInstance, route_status: RouteStatus, next_node: int, is_customer: bool) -> None:
    """Updates the route status with the next node."""
    distance = instance.distance(route_status.current_location, next_node)
    energy_used = instance.energy_consumption(route_status.current_location, next_node)

    route_status.total_distance += distance
    route_status.remaining_energy -= energy_used

    arrival_time = route_status.last_service_end_time + distance
    route_status.arrival_time = arrival_time
    route_status.current_location = next_node
    route_status.route.append(next_node)

    if is_customer:
        route_status.remaining_capacity -= instance.demand(next_node)
        start_service = max(arrival_time, instance.ready(next_node))
        end_service = start_service + instance.service_time(next_node)
        route_status.last_service_end_time = end_service
    else:
        recharge_amount = instance.vehicle_energy_capacity - route_status.remaining_energy
        recharge_time = instance.time_for_recharging_energy(recharge_amount)
        end_recharge = arrival_time + recharge_time
        route_status.remaining_energy = instance.vehicle_energy_capacity
        route_status.last_service_end_time = end_recharge

def get_feasible_customers(instance: EVRPTWInstance, route: RouteStatus, unserved_customers: set[int]) -> dict[int, Optional[int]]:
    """
    Returns the feasible customers that can be served next.
    The return value is a dictionary where:
    - customer_id - None: if directly reachable and depot can be reached after
    - customer_id - station_id: if customer is only reachable after visiting the given station
    """
    feasible_customers = {}

    for cid in unserved_customers:
        if route.remaining_capacity < instance.demand(cid):
            continue # Cannot serve this customer due to capacity constraints

        arrival_time = route.last_service_end_time + instance.travel_time(route.current_location, cid)
        if arrival_time > instance.due(cid):
            continue # Cannot serve this customer due to time window constraints

        energy_needed = instance.energy_consumption(route.current_location, cid)
        if energy_needed <= route.remaining_energy: # Directly reachable customer
            remaining_after_serve = route.remaining_energy - energy_needed
            if can_reach_depot(instance, cid, remaining_after_serve): # Can reach depot after serving this customer
                feasible_customers[cid] = None # We do not need a station before this customer
                continue

        station_id = find_best_station_before_customer(instance, route, cid)
        if station_id is not None: # If we need to visit a station and we can reach it
            feasible_customers[cid] = station_id

    return feasible_customers

def handle_no_feasible_customers(instance: EVRPTWInstance, route_status: RouteStatus) -> bool:
    """
    Handles the case when no feasible customers are available:
    1. Check if we can return to depot directly.
    2. If not, find the nearest station and recharge.
    Returns True if we can continue, False if the route can be closed.
    """
    energy_to_depot = instance.energy_consumption(route_status.current_location, instance.depot_id)
    if route_status.remaining_energy >= energy_to_depot: # We can return to depot directly
        return False

    nearest_station = find_nearest_station(instance, route_status.current_location, route_status.remaining_energy)
    if nearest_station is None: # No station is reachable with the remaining energy
        return False  

    # If we found a station, we are going to there
    update_route_status(instance, route_status, nearest_station, is_customer=False)
    return True

def find_best_station_before_customer(instance: EVRPTWInstance, route_status: RouteStatus, customer_node: int) -> Optional[int]:
    """Finds the best station to visit before serving a customer."""
    best_station = None
    best_total_distance = float('inf')

    for sid in instance.station_ids:
        energy_to_station = instance.energy_consumption(route_status.current_location, sid)
        if energy_to_station > route_status.remaining_energy: 
            continue # Cannot reach this station

        energy_station_to_customer = instance.energy_consumption(sid, customer_node)
        if energy_station_to_customer > instance.vehicle_energy_capacity: 
            continue # Cannot reach customer from this station

        arrival_to_station = route_status.last_service_end_time + instance.travel_time(route_status.current_location, sid)
        recharge_amount = instance.vehicle_energy_capacity - (route_status.remaining_energy - energy_to_station)
        departure_from_station = arrival_to_station + instance.time_for_recharging_energy(recharge_amount)

        arrival_to_customer = departure_from_station + instance.travel_time(sid, customer_node)
        if arrival_to_customer > instance.due(customer_node):
            continue # Cannot arrive in the time window of the customer after visiting this station

        energy_after_customer = instance.vehicle_energy_capacity - energy_station_to_customer
        if not can_reach_depot(instance, customer_node, energy_after_customer):
            continue # Cannot reach depot after serving this customer

        # We would like to minimize the total distance traveled
        total_distance = instance.distance(route_status.current_location, sid) + instance.distance(sid, customer_node)
        if total_distance < best_total_distance:
            best_total_distance = total_distance
            best_station = sid

    return best_station

def can_reach_depot(instance: EVRPTWInstance, from_node: int, remaining_energy: float) -> bool:
    """Checks if we can reach the depot from a given node with the remaining energy."""
    direct_energy = instance.energy_consumption(from_node, instance.depot_id)
    if direct_energy <= remaining_energy: # We can reach depot directly
        return True

    for sid in instance.station_ids:
        energy_to_station = instance.energy_consumption(from_node, sid)
        energy_station_to_depot = instance.energy_consumption(sid, instance.depot_id)
        if energy_to_station <= remaining_energy: # We can reach this station
            if energy_station_to_depot <= instance.vehicle_energy_capacity: # We can reach depot from this station
                return True
            
    return False # No station allows us to reach depot with the remaining energy

def find_nearest_station(instance: EVRPTWInstance, from_node: int, remaining_energy: float) -> Optional[int]:
    """Finds the nearest station that can be reached with the remaining energy."""
    best_station = None
    min_distance = float('inf')

    for sid in instance.station_ids:
        distance = instance.distance(from_node, sid)
        if instance.energy_consumption(from_node, sid) <= remaining_energy and distance < min_distance:
            min_distance = distance
            best_station = sid

    return best_station

def finish_route(route_status: RouteStatus, instance: EVRPTWInstance) -> bool:
    """If the route is not finished, it tries to return to depot or a station."""
    if not try_return_to_depot(route_status, instance):
        return False 
    update_route_status(instance, route_status, instance.depot_id, is_customer=False)
    return True

def try_return_to_depot(route_status: RouteStatus, instance: EVRPTWInstance) -> bool:
    """Checks if we can return to depot directly or via a station."""
    if can_reach_depot(instance, route_status.current_location, route_status.remaining_energy):
        return True # We can return to depot directly

    station_id = find_nearest_station(instance, route_status.current_location, route_status.remaining_energy)
    if station_id is None:
        return False # No station is reachable with the remaining energy

    update_route_status(instance, route_status, station_id, is_customer=False)

    # If we find a station, we check if we can reach depot after recharging
    return can_reach_depot(instance, route_status.current_location, route_status.remaining_energy)
