from __future__ import annotations

from typing import List, Optional, Tuple


def repair_key_bitting_bellman_ford(
    x: List[int],
    d_min: int,
    d_max: int,
    macs: int,
    station_max_ceiling: Optional[List[Optional[int]]] = None,
    forbidden_positions: Optional[List[int]] = None,
    no_cut_mask: Optional[List[bool]] = None,
    min_first_station_index: Optional[int] = None,
    max_consecutive_repeats: Optional[int] = None
) -> Tuple[bool, Optional[List[int]], str]:
    """
    Repair key bitting using difference constraints solved via Bellman-Ford.
    
    We transform the problem into finding minimum values that satisfy:
    - y[i] >= x[i] (deepening only)
    - y[i] <= ceiling[i] (upper bounds)
    - |y[i+1] - y[i]| <= macs (MACS constraints)
    
    Since Bellman-Ford finds shortest paths (minimums), and we want to minimize
    deepening, this is perfect for our use case.
    """
    n = len(x)
    
    for i in range(n):
        if x[i] < d_min or x[i] > d_max:
            return False, None, "exceeds maximum depth, cannot fix by deepening"
    
    effective_ceiling = [d_max] * n
    if station_max_ceiling:
        for i in range(min(n, len(station_max_ceiling))):
            if station_max_ceiling[i] is not None:
                effective_ceiling[i] = min(effective_ceiling[i], station_max_ceiling[i])
    
    for i in range(n):
        if x[i] > effective_ceiling[i]:
            return False, None, "station-specific ceiling violated"
    
    is_forbidden = [False] * n
    if forbidden_positions:
        for pos in forbidden_positions:
            if 0 <= pos < n:
                is_forbidden[pos] = True
    if no_cut_mask:
        for i in range(min(n, len(no_cut_mask))):
            if no_cut_mask[i]:
                is_forbidden[i] = True
    if min_first_station_index is not None:
        for i in range(min(n, min_first_station_index)):
            is_forbidden[i] = True
    
    for i in range(n):
        if is_forbidden[i] and x[i] > d_min - 1:
            if min_first_station_index is not None and i < min_first_station_index:
                return False, None, "first station not allowed for this stop type"
            return False, None, "forbidden/no-cut station cut present"
    
    y = x[:]
    
    max_iterations = n * n  # Enough for convergence
    for iteration in range(max_iterations):
        changed = False
        
        for i in range(n - 1):
            if y[i + 1] < y[i] - macs:
                new_val = y[i] - macs
                if is_forbidden[i + 1]:
                    return False, None, "cannot satisfy MACS and constraints via deepening-only"
                if new_val > effective_ceiling[i + 1]:
                    return False, None, "cannot satisfy MACS and constraints via deepening-only"
                if new_val > y[i + 1]:
                    y[i + 1] = new_val
                    changed = True
        
        for i in range(n - 2, -1, -1):
            if y[i] < y[i + 1] - macs:
                new_val = y[i + 1] - macs
                if is_forbidden[i]:
                    return False, None, "cannot satisfy MACS and constraints via deepening-only"
                if new_val > effective_ceiling[i]:
                    return False, None, "cannot satisfy MACS and constraints via deepening-only"
                if new_val > y[i]:
                    y[i] = new_val
                    changed = True
        
        if not changed:
            break
    
    for i in range(n):
        if y[i] < x[i]:
            return False, None, "internal error: solution violates deepening constraint"
        if y[i] > effective_ceiling[i]:
            return False, None, "cannot satisfy ceiling constraints"
        if is_forbidden[i] and y[i] != x[i]:
            return False, None, "internal error: forbidden position changed"
    
    for i in range(n - 1):
        if abs(y[i + 1] - y[i]) > macs:
            return False, None, "cannot satisfy MACS and constraints via deepening-only"
    
    if max_consecutive_repeats is not None:
        count = 1
        for i in range(1, n):
            if y[i] == y[i - 1]:
                count += 1
                if count > max_consecutive_repeats:
                    return False, None, "too many consecutive repeats of same cut"
            else:
                count = 1
    
    return True, y, "repairable to a valid bitting by deepening"


def is_terminally_invalid_bellman_ford_final(
    seq: List[int],
    d_min: int,
    d_max: int,
    macs: int,
    length: int,
    station_max_ceiling: Optional[List[Optional[int]]] = None,
    forbidden_positions: Optional[List[int]] = None,
    no_cut_mask: Optional[List[bool]] = None,
    min_first_station_index: Optional[int] = None,
    max_consecutive_repeats: Optional[int] = None
) -> Tuple[bool, str]:
    """Check if bitting is terminally invalid."""
    if len(seq) != length:
        return True, "length mismatch"
    
    if max_consecutive_repeats is not None:
        count = 1
        for i in range(1, len(seq)):
            if seq[i] == seq[i - 1]:
                count += 1
                if count > max_consecutive_repeats:
                    return True, "too many consecutive repeats of same cut"
            else:
                count = 1
    
    feasible, _, reason = repair_key_bitting_bellman_ford(
        seq, d_min, d_max, macs, station_max_ceiling,
        forbidden_positions, no_cut_mask, min_first_station_index,
        max_consecutive_repeats
    )
    
    return not feasible, reason
