def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x, y):
        return abs(x - ox) + abs(y - oy)

    def obs_pen(x, y):
        if (x, y) in obs:
            return 50.0
        # Strong penalty near obstacles to avoid zigzag traps
        p = 0
        for (ax, ay) in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 50.0
            if d <= 2:
                p += (3 - d) * 2
        return float(p)

    def edge_score(x, y):
        # Prefer staying away from edges a bit (helps against zigzags)
        m = min(x, y, w - 1 - x, h - 1 - y)
        return float(m)

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = manhattan(nx, ny)
        o = obs_pen(nx, ny)
        e = edge_score(nx, ny)
        if not is_evader:
            # Pursuer: minimize distance, heavily prefer capture
            val = (-10.0 * (1.0 if d == 0 else 0.0)) + (-2.0 * d) - 2.5 * o + 0.05 * e
        else:
            # Evader: maximize distance, strongly avoid obstacles
            val = (10.0 * (1.0 if d > 0 else 0.0)) + (2.2 * d) - 3.0 * o + 0.02 * e
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]