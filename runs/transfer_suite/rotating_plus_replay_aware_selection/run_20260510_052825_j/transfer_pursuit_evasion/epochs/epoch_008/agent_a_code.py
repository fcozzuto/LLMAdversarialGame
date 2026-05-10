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
    if not pursuer:
        if is_pursuer(opp_role) and not is_evader(opp_role):
            pursuer = True
        elif is_pursuer(opp_role) and is_evader(opp_role):
            pursuer = False
    if pursuer and is_evader(self_role):
        pursuer = False

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    targets = [(0,0),(w-1,0),(w-1,h-1),(0,h-1)]
    t = targets[observation.get("turn_index", 0) % 4]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx*ddx + ddy*ddy

        if pursuer:
            base = -dist2  # minimize distance
        else:
            base = dist2   # maximize distance

        # mild corner bias to reduce dithering
        corner_dx, corner_dy = nx - t[0], ny - t[1]
        corner_dist2 = corner_dx*corner_dx + corner_dy*corner_dy
        bias = corner_dist2 if not pursuer else -corner_dist2

        # wall/obstacle avoidance penalty (encourage moves with more free neighbors)
        free = 0
        for ax, ay in deltas:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) not in obs:
                free += 1

        val = base + (0.06 * bias) + (0.02 * free)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move