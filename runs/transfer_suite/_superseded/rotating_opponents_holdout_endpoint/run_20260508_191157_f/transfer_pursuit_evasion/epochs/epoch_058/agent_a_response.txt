def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curd = man(sx, sy, ox, oy)

    # Deterministic tie-break order: prefer smaller dx, then dy
    best = None
    best_score = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        nd = man(nx, ny, ox, oy)
        if role == "pursuer":
            # Primary: reduce distance; Secondary: avoid moving "toward" obstacles by penalizing closeness to them
            prox_obs = min((abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs_set), default=99)
            score = (nd, -prox_obs)
        else:
            # Evader: maximize distance
            prox_obs = min((abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs_set), default=99)
            score = (-nd, -prox_obs)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    # If fully blocked, fall back to staying still
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]