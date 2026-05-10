def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}
    roles = (observation.get("self_role", ""), observation.get("opponent_role", ""))
    self_role = roles[0].lower()
    is_evader = ("evad" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    is_pursuer = ("purs" in self_role) or ("seeker" in self_role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_pos(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Keep away from obstacles' proximity a bit (deterministic)
        prox = 0
        for (ax, ay) in obs_set:
            dd = (nx - ax) * (nx - ax) + (ny - ay) * (ny - ay)
            if dd == 0:
                prox += 10
            else:
                prox += 1.0 / (dd)
        if is_pursuer:
            # Prefer smaller distance; tie-break toward center slightly to avoid oscillation near walls
            score = -d2 - 0.05 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) - 0.2 * prox
        else:
            # Prefer larger distance; also prefer staying toward center to avoid corner traps
            score = d2 + 0.05 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) - 0.2 * prox
        if best is None or (score > best_score):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]