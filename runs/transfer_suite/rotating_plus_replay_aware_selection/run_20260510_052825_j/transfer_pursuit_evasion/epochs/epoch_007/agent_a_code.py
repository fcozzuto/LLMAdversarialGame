def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = (role or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = (role or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role) and not is_evader(opp_role):
        pursuer = False
    elif not pursuer and is_pursuer(opp_role) and is_evader(opp_role):
        pursuer = True
    elif pursuer and is_evader(self_role):
        pursuer = False

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx*ddx + ddy*ddy

        # Obstacle-aware term: stay away from obstacle-adjacent cells.
        prox = 0
        for ax, ay in obstacles:
            adx, ady = abs(nx - ax), abs(ny - ay)
            if adx <= 1 and ady <= 1:
                prox += 1

        # Corner bias to reduce zigzag escape when pursuing; inverse when evading.
        corner_dist = (nx*(w-1-nx)) + (ny*(h-1-ny))
        # smaller corner_dist => near corner
        near_corner = (w-1) * (h-1) - corner_dist

        # If evader, also bias against moves that approach opponent by too much.
        if pursuer:
            val = dist2 + 2.5*prox - 0.15*near_corner
            better = (best_val is None) or (val < best_val)
        else:
            val = -dist2 + 2.5*prox - 0.10*near_corner
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best