def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    role = (observation.get("self_role", "") or "").lower()
    pursue = ("purs" in role) or ("pursuer" in role) or ("chase" in role)
    if "evad" in role and "purs" not in role:
        pursue = False

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Target waypoint: push toward farthest corner when evading, otherwise toward a corner/greedy path when pursuing.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if pursue:
        # Alternate between two opposite corners to reduce wall-running traps.
        phase = int(observation.get("turn_index", 0)) % 2
        target = corners[phase * 2 + (0 if ox < (w - 1) / 2 else 1)]
    else:
        # Pick corner farthest from opponent.
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
        target = (tx, ty)

    best_move = [0, 0]
    best_val = None

    def score(nx, ny):
        # Distance to opponent dominates; second term nudges toward/away from waypoint.
        d_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_t = (nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1])
        # Obstacle proximity penalty to avoid getting stuck near walls.
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    near += 1
        # Prefer moving to reduce near when evading; when pursuing, avoid getting blocked.
        if pursue:
            return (-d_o) + (-0.02 * d_t) + (-0.15 * near)
        else:
            return (d_o) + (0.01 * d_t) + (-0.10 * near)

    # Deterministic tie-break: choose lexicographically smallest move among best.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = score(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]