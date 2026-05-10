def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score(nx, ny):
        dx = nx - ox
        dy = ny - oy
        d = (dx * dx + dy * dy)
        return d

    best = None
    best_key = None
    eps = 1e-9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = score(nx, ny)
        # Tie-break deterministically: prefer closer to opponent if pursuer, farther if evader
        # Also lightly prefer staying away from obstacles' vicinity to reduce boundary/stall effects.
        adj = 0
        for ox2, oy2 in obstacles:
            if abs(nx - ox2) <= 1 and abs(ny - oy2) <= 1:
                adj += 1
        if i_am_pursuer:
            key = (d2, adj, nx, ny)
        else:
            key = (-d2, adj, -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is not None:
        return [int(best[0]), int(best[1])]

    # If all moves invalid, return deterministic stay
    return [0, 0]