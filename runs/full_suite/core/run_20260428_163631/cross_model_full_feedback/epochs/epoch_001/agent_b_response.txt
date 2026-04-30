def choose_move(observation):
    # Simple deterministic strategy:
    # 1) Move toward the nearest resource not currently occupied by obstacle/agent.
    # 2) If no resources left or blocked, chase opponent's position while keeping safe distance.
    # 3) Never leave grid bounds; clamp moves; always return a valid delta in {-1,0,1}.
    turn_index = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    # Build a set for quick lookup
    obs_set = {tuple(p) for p in obstacles}
    res_list = [tuple(p) for p in resources]
    sx, sy = self_pos
    # helper to clamp
    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v
    # If there are resources available, target the closest not blocked by obstacle
    best_r = None
    best_dist = 10**9
    for r in res_list:
        if r in obs_set: 
            continue
        dx = r[0] - sx
        dy = r[1] - sy
        dist = abs(dx) + abs(dy)
        if dist < best_dist:
            best_dist = dist
            best_r = r
    if best_r is not None:
        dx = best_r[0] - sx
        dy = best_r[1] - sy
        move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        nx = clamp(sx + move_x, 0, w - 1)
        ny = clamp(sy + move_y, 0, h - 1)
        return [nx - sx, ny - sy]
    # If no resources, approach opponent but maintain at least distance 1 if possible
    dx = opp_pos[0] - sx
    dy = opp_pos[1] - sy
    if dx == 0 and dy == 0:
        # same square, stay
        return [0, 0]
    move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    # Try to move away if currently adjacent and could collide with obstacle or wall
    nx = clamp(sx + move_x, 0, w - 1)
    ny = clamp(sy + move_y, 0, h - 1)
    if (nx, ny) in obs_set:
        # try alternative step
        alt_x = 0 if dx == 0 else (-1 if dx > 0 else 1)
        alt_y = 0 if dy == 0 else (-1 if dy > 0 else 1)
        nx2 = clamp(sx + alt_x, 0, w - 1)
        ny2 = clamp(sy + alt_y, 0, h - 1)
        if (nx2, ny2) not in obs_set:
            return [nx2 - sx, ny2 - sy]
    return [nx - sx, ny - sy]