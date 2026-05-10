def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_obs_dist(x, y):
        if not obs:
            return 99
        d = 99
        for bx, by in obs:
            dd = man(x, y, bx, by)
            if dd < d:
                d = dd
        return d

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d = man(nx, ny, ox, oy)
        dobs = min_obs_dist(nx, ny)
        corner_metric = max(man(nx, ny, cx, cy) for cx, cy in corners)

        if is_pursuer:
            # Prefer moves that reduce distance; avoid getting too close to obstacles (to avoid being trapped).
            score = (-d * 10) + (dobs * 0.6) + (corner_metric * -0.02)
        else:
            # Evader: increase distance; keep away from obstacles; bias toward farthest corner.
            score = (d * 10) + (dobs * 0.7) + (corner_metric * 0.03)

        if best is None or (score > best_score):
            best_score = score
            best = [dx, dy]

    if best is None:
        # If all moves were invalid due to obstacles/bounds, try staying deterministic.
        return [0, 0]
    return best