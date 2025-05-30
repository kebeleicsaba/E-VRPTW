from dataclasses import dataclass
from typing import List

@dataclass
class RouteStatus:
    current_location: int
    remaining_capacity: float
    remaining_energy: float
    arrival_time: float
    last_service_end_time: float
    route: List[int]
    total_distance: float