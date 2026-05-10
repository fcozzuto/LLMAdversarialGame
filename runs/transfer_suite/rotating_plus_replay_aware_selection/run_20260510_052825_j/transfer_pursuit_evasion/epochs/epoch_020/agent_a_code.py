def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def is_ev(r):
        r = (r or "").lower().replace("-", "_")
        return ("evad" in r) or (r == "evader")
    def is_pu(r):
        r = (r or "").lower().replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    self_role = (observation.get("self_role") or "")
    opponent_role = (observation.get("opponent_role") or "")
    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opponent_role) and not is_ev(opponent_role):
        pursuer = False
    else:
        pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def clamp_free(x, y):
        if not inb(x, y): 
            return False
        return (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    # Obstacle influence: prefer moving away from obstacle-adjacent squares (avoid getting funneled).
    def obs_pen(x, y):
        pen = 0
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obs:
                pen += 3
        return pen

    best = None
    best_val = -10**18 if pursuer else 10**18
    # Deterministic tie-breaker based on turn parity and move ordering.
    parity = int(observation.get("turn_index", 0)) & 1

    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not clamp_free(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        # Pursuer: maximize progress to opponent, minimize obstacle penalty.
        # Evader: maximize distance, while also avoiding obstacle-adjacent squares.
        val = (-dist if pursuer else dist) + (obs_pen(nx, ny) * (1 if pursuer else 1)) + (0.001 * ((i + parity) % 2))
        # For pursuer we want minimal val; for evader we want maximal dist but same sign handled above.
        # Convert to selection metric:
        metric = (-val) if pursuer else val
        if best is None or metric > best_val:
            best_val = metric
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]