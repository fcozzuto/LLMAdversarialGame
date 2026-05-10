def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer_self = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    pursuer_opp = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = pursuer_self or (not pursuer_opp)
    best = None
    best_val = -10**18
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ddx = nx - ox
        ddy = ny - oy
        d2 = ddx * ddx + ddy * ddy
        val = -d2 if pursue else d2
        if val > best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]