def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = observation.get("self_role", "")
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obs_set = {(int(a[0]), int(a[1])) for a in obstacles if len(a) >= 2}
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    pursuer = ("purs" in self_role.lower()) or ("hunter" in self_role.lower())
    best = None
    best_val = None

    # Deterministic tie-breaker prefers earlier in deltas for equal objective.
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if pursuer:
            val = dist2(nx, ny, ox, oy)
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        else:
            # Evader: maximize distance from pursuer.
            val = dist2(nx, ny, ox, oy)
            # Avoid moving into pursuer if capture is possible.
            if nx == ox and ny == oy:
                val = -10**18
            if best_val is None or val > best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]