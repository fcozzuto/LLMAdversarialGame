def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    self_role = observation.get("self_role", "")
    opponent_role = observation.get("opponent_role", "")
    is_pursuer = (self_role == "pursuer") or ("pursuer" in self_role and "evader" in opponent_role) or ("pursuer" in self_role)
    # Candidate moves (deterministic order)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # If grid edges are used, clamp by engine (but still avoid obviously invalid positions)
    best = None
    best_val = None
    def score(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev distance
        if is_pursuer:
            return -d  # maximize negative distance == minimize distance
        else:
            return d   # maximize distance
    # Secondary tie-breaker: prefer moving along the main direction
    dirx = 0 if ox == sx else (1 if ox > sx else -1)
    diry = 0 if oy == sy else (1 if oy > sy else -1)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        val = score(nx, ny)
        # Tie-break: align with direction; if evader, align away (reverse for tie-break only)
        align = dx * dirx + dy * diry
        if not is_pursuer:
            align = -align
        # Prefer higher align when val ties
        key = (val, align, -(abs(nx - sx) + abs(ny - sy)))
        if best is None or key > best_val:
            best_val = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best