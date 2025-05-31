from random import Random

from .alns_state import ALNSState

def dummy_destroy(state: ALNSState, rnd: Random, **kwargs) -> ALNSState:
    return state.copy()