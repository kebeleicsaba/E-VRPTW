import json
from pathlib import Path

from model import EVRPTWInstance, RouteStatus

def select_next_customer(instance: EVRPTWInstance, route_status: RouteStatus, feasible_customers: list[int]) -> int | None:
    customer_costs = {
        cid: customer_cost(instance, route_status, cid)
        for cid in feasible_customers
    }
    return min(customer_costs, key=customer_costs.get, default=None)

def customer_cost(instance: EVRPTWInstance, route_status: RouteStatus, cid: int) -> float:
    travel_time = instance.travel_time(route_status.current_location, cid)
    arrival_time = route_status.last_service_end_time + travel_time
    ready_time = instance.ready(cid)
    wait_time = max(0, ready_time - arrival_time)
    distance = instance.distance(route_status.current_location, cid)

    construction_config = load_construction_config()

    return distance + wait_time * construction_config["wait_time_weight"]

def load_construction_config():
    config_path = Path(__file__).parent.parent / "config" / "construction_config.json"
    with open(config_path) as f:
        return json.load(f)

# Old ideas
def customer_cost_time(instance: EVRPTWInstance, route_status: RouteStatus, cid: int) -> float:
    travel_time = instance.travel_time(route_status.current_location, cid)
    arrival_time = route_status.last_service_end_time + travel_time
    ready_time = instance.ready(cid)
    wait_time = max(0, ready_time - arrival_time)
    return arrival_time + wait_time 

def customer_cost_distance(instance: EVRPTWInstance, route_status: RouteStatus, cid: int) -> float:
    return instance.distance(route_status.current_location, cid)