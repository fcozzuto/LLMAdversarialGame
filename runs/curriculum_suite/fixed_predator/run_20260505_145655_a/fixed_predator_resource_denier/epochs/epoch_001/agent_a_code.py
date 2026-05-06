def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_val = None

    # Precompute resource targets (deterministic)
    res_list = resources[:]
    res_list.sort(key=lambda p: (p[0], p[1]))

    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    if not res_list:
        tx, ty = w//2, h//2
        cx, cy = sx, sy
        best_dx, best_dy = 0, 0
        best_d = None
        for dx, dy in moves:
            nx, ny = clamp(cx + dx, 0, w-1), clamp(cy + dy, 0, h-1)
            if (nx, ny) in obs_set:
                nx, ny = cx, cy
            d = (nx - tx)*(nx - tx) + (ny - ty)*(ny - ty)
            if best_d is None or d < best_d:
                best_d = d
                best_dx, best_dy = dx, dy
        return [best_dx, best_dy]

    cx, cy = sx, sy
    for dx, dy in moves:
        nx, ny = clamp(cx + dx, 0, w-1), clamp(cy + dy, 0, h-1)
        if (nx, ny) in obs_set:
            nx, ny = cx, cy  # mirror engine behavior
        # Distance to nearest resource (prefer)
        nd2 = None
        tr = None
        for rx, ry in res_list:
            d2 = (nx - rx)*(nx - rx) + (ny - ry)*(ny - ry)
            if nd2 is None or d2 < nd2 or (d2 == nd2 and (rx, ry) < tr):
                nd2, tr = d2, (rx, ry)
        # Denial pressure: if opponent is closer to the same area, increase separation
        od2 = (ox - tr[0])*(ox - tr[0]) + (oy - tr[1])*(oy - tr[1])
        my_d2 = (nx - tr[0])*(nx - tr[0]) + (ny - tr[1])*(ny - tr[1])
        # Opponent distance (stay away slightly unless we are clearly closer to target)
        opp_dist2 = (nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)
        # Capture blocking: if we can get within 1 of a resource, prioritize strongly
        near_bonus = 0
        if nd2 <= 1:  # adjacent or on resource
            near_bonus = 5.0
        # Score components
        val = (-nd2) + near_bonus
        # If we are behind opponent toward target, prioritize separation
        if my_d2 > od2:
            val += 0.02 * opp_dist2
        else:
            val -= 0.01 * (64 - min(opp_dist2, 64))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]