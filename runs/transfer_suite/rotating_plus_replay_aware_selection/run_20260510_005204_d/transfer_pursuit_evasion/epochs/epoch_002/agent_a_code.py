def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in self_role) or ("runner" in self_role) or ("escape" in self_role)
    is_pursuer = ("purs" in self_role) or ("seeker" in self_role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_pos(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx*dx + dy*dy

    # For deterministic tie-breaking: fixed order already in moves.
    best_move = [0, 0]
    best_val = None

    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)

        # Obstacle penalty: discourage moving close to obstacles.
        prox_pen = 0.0
        for ax, ay in obs_set:
            dd = dist2(nx, ny, ax, ay)
            if dd == 0:
                prox_pen += 1e9
            else:
                prox_pen += 1.0 / (dd + 1e-9)

        # Capture (distance 0) is immediately terminal; prioritize when pursuer.
        if is_pursuer and d_opp == 0:
            val = 1e18
        else:
            # If pursuer: prefer smaller opponent distance and moving roughly toward opponent.
            # If evader: prefer larger opponent distance and moving away.
            if is_pursuer:
                val = (-d_opp) + (-0.15 * d_tgt) - (0.5 * prox_pen)
            else:
                val = (d_opp) + (0.02 * d_tgt) - (0.7 * prox_pen)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move