from dataclasses import dataclass
from enum import Enum, auto

@dataclass(slots=True)
class Coordinate:
    x: float
    y: float

class NodeKind(Enum):
    Depot = auto()
    Station = auto()
    Customer = auto()

@dataclass(slots=True)
class Node:
    kind: NodeKind
    string_id: str
    coordinates: Coordinate
    demand: float
    ready: float
    due: float
    service_time: float

@dataclass()
class EVRPTWInstance:
    num_stations: int
    num_customers: int
    num_nodes: int
    nodes: list[Node]
    vehicle_load_capacity: float # max demand served
    vehicle_energy_capacity: float # max energy
    vehicle_energy_consumption: float # distance -> energy
    inverse_recharging_rate: float # time -> energy
    distances: list[float]

    # For quick access
    customer_ids: list[int] = None
    station_ids: list[int] = None
    depot_id: int = None

    def __post_init__(self):
        self.customer_ids = []
        self.station_ids = []

        for i, node in enumerate(self.nodes):
            if node.kind == NodeKind.Customer:
                self.customer_ids.append(i)
            elif node.kind == NodeKind.Station:
                self.station_ids.append(i)
            elif node.kind == NodeKind.Depot:
                self.depot_id = i

    def distance(self, u: int, v: int) -> float:
        return self.distances[u * self.num_nodes + v]

    def travel_time(self, u: int, v: int) -> float:
        return self.distances[u * self.num_nodes + v]

    def energy_consumption(self, u: int, v: int) -> float:
        return self.distances[u * self.num_nodes + v] * self.vehicle_energy_consumption

    def time_for_recharging_energy(self, amount: float) -> float:
        return amount * self.inverse_recharging_rate

    def amount_recharged_in_time(self, time: float) -> float:
        return time / self.inverse_recharging_rate

    def demand(self, u: int) -> float:
        return self.nodes[u].demand

    def ready(self, u: int) -> float:
        return self.nodes[u].ready

    def due(self, u: int) -> float:
        return self.nodes[u].due

    def service_time(self, u: int) -> float:
        return self.nodes[u].service_time

    def is_depot(self, u: int) -> bool:
        return self.nodes[u].kind == NodeKind.Depot

    def is_station(self, u: int) -> bool:
        return self.nodes[u].kind == NodeKind.Station

    def is_customer(self, u: int) -> bool:
        return self.nodes[u].kind == NodeKind.Customer