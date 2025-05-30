import math
from pathlib import Path

from model.instance import EVRPTWInstance, Node, NodeKind, Coordinate

def parse_node_kind(string: str) -> NodeKind:
    if string == "d":
        return NodeKind.Depot
    elif string == "f":
        return NodeKind.Station
    elif string == "c":
        return NodeKind.Customer
    else:
        raise ValueError(f"Unknown node kind {string}")

# StringID   Type       x          y          demand     ReadyTime  DueDate    ServiceTime
# D0         d          40.0       50.0       0.0        0.0        1236.0     0.0
# S0         f          40.0       50.0       0.0        0.0        1236.0     0.0
# ...
# C96        c          60.0       80.0       10.0       177.0      243.0      90.0
#
# Q Vehicle fuel tank capacity /77.75/
# C Vehicle load capacity /200.0/
# r fuel consumption rate /1.0/
# g inverse refueling rate /3.47/
# v average Velocity /1.0/
def read_evrptw_instance(filepath: Path) -> EVRPTWInstance:
    with open(filepath, 'r') as f:
        lines = f.readlines()
        # find first empty row (separates the node list from the other parameters
        u = 1
        nodes = list()
        while True:
            line = lines[u].strip()
            if line == "":
                break
            # else read node
            split = line.split()
            nodes.append(Node(
                string_id=split[0],
                kind=parse_node_kind(split[1]),
                coordinates=Coordinate(x=float(split[2]), y=float(split[3])),
                demand=float(split[4]),
                ready=float(split[5]),
                due=float(split[6]),
                service_time=float(split[7])
            ))
            u = u + 1

        assert len(lines) >= u + 5 # there should be at least 4 more lines

        def get_property_from_line(line: str):
            # Q Vehicle fuel tank capacity /77.75/
            return line.split("/")[1]

        vehicle_energy_capacity = float(get_property_from_line(lines[u+1]))
        vehicle_load_capacity = float(get_property_from_line(lines[u+2]))
        vehicle_energy_consumption = float(get_property_from_line(lines[u+3]))
        inverse_recharging_rate = float(get_property_from_line(lines[u+4]))

        num_stations = sum(1 if node.kind == NodeKind.Station else 0 for node in nodes)
        num_customers = sum(1 if node.kind == NodeKind.Customer else 0 for node in nodes)
        num_nodes = len(nodes)
        assert num_nodes == num_stations + num_customers + 1

        def get_euclidean_distance(u: Node, v: Node) -> float:
            return math.sqrt((u.coordinates.x - v.coordinates.x)**2 + (u.coordinates.y - v.coordinates.y)**2)

        distances = [0.0] * (num_nodes*num_nodes)
        for (u,n1) in enumerate(nodes):
            for (v,n2) in enumerate(nodes):
                if n1 != n2:
                    distances[u*num_nodes + v] = get_euclidean_distance(n1,n2)

        return EVRPTWInstance(
            num_stations=num_stations,
            num_customers=num_customers,
            num_nodes=num_nodes,
            nodes=nodes,
            vehicle_load_capacity=vehicle_load_capacity,
            vehicle_energy_capacity=vehicle_energy_capacity,
            vehicle_energy_consumption=vehicle_energy_consumption,
            inverse_recharging_rate=inverse_recharging_rate,
            distances=distances
        )
