from pathlib import Path

from model.instance import EVRPTWInstance

class Solution:
    def __init__(self, routes: list[list[int]] = None) -> None:
        self.routes = routes if routes else []
        self.total_distance = 0

    def compute_total_distance(self, instance: EVRPTWInstance) -> float:
        self.total_distance = sum(
            instance.distance(route[i], route[i+1])
            for route in self.routes
            for i in range(len(route)-1)
        )
        return self.total_distance

    def copy(self) -> 'Solution':
        return Solution(routes=[list(route) for route in self.routes])
    
    def __str__(self) -> str:
        return f"Solution:\nRoutes={self.routes}\nTotal distance={self.total_distance}"
    
    def pretty_print(self, instance: EVRPTWInstance) -> str:
        lines = [f"Total distance: {self.total_distance:.3f}", "Routes:"]

        for r_idx, route in enumerate(self.routes):
            lines.append(f"  Route {r_idx + 1}:")

            capacity = instance.vehicle_load_capacity
            soc = instance.vehicle_energy_capacity  # State of charge
            time = 0.0
            last_node = route[0]

            lines.append(
                f"    Start at {instance.nodes[last_node].string_id} | Capacity: {capacity}, Energy: {soc:.1f}, Time: {time:.1f}"
            )

            for node in route[1:]:
                demand = instance.demand(node) if instance.is_customer(node) else 0
                distance = instance.distance(last_node, node)
                travel_time = instance.travel_time(last_node, node)
                energy_used = instance.energy_consumption(last_node, node)

                arrival_time = time + travel_time
                soc_on_arrival = soc - energy_used
                energy_feasible = soc_on_arrival > 0.0

                type_str = "Station" if instance.is_station(node) else "Customer" if instance.is_customer(node) else "Depot"

                warning = ""
                if not energy_feasible:
                    warning = f" ⚠ ENERGY VIOLATION (SOC={soc_on_arrival:.3f})"

                if instance.is_customer(node):
                    ready = instance.ready(node)
                    due = instance.due(node)
                    service_time = instance.service_time(node)
                    start_service = max(arrival_time, ready)
                    end_service = start_service + service_time

                    time = end_service
                    capacity -= demand
                    soc = soc_on_arrival

                    tw_status = ""
                    if start_service > due:
                        tw_status = "⚠ Late"
                    elif start_service < ready:
                        tw_status = "⚠ Early"

                    tw_info = f" | TW: [{ready}, {due}], Arrival: {arrival_time:.1f}, Start: {start_service:.1f}{' ' + tw_status if tw_status else ''}"
                elif instance.is_station(node):
                    recharge_amount = instance.vehicle_energy_capacity - max(0.0, soc_on_arrival)
                    recharge_time = instance.time_for_recharging_energy(recharge_amount)
                    time = arrival_time + recharge_time
                    soc = instance.vehicle_energy_capacity  # fully recharged
                    tw_info = f" | Arrival: {arrival_time:.1f}, Recharge: {recharge_amount:.1f} → Full"
                else:  # Depot
                    time = arrival_time
                    soc = soc_on_arrival
                    tw_info = f" | Arrival: {arrival_time:.1f}"

                lines.append(
                    f"    → {node} ({type_str}) | Dist: {distance:.1f}, Cap: {capacity}, Energy: {soc:.1f}, Time: {time:.1f}{tw_info}{warning}"
                )

                last_node = node

        print("\n".join(lines))

