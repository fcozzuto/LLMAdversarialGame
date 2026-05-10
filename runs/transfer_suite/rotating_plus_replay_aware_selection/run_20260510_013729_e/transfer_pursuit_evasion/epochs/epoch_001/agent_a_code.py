def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    r_self = (observation.get("self_role", "") or "").lower()
    r_opp = (observation.get("opponent_role", "") or "").lower()
    pursuer = "purs" in r_self or ("pursuer" in r_self) or (r_opp == "")
    if not (("purs" in r_self) or ("pursuer" in r_self)) and ("purs" in r_opp):
        pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if pursuer:
            val = -d2  # maximize closeness (i.e., minimize distance)
        else:
            val = d2   # maximize distance
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best