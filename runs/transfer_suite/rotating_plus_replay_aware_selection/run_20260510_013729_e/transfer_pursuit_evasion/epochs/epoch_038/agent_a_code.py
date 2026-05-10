def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_obst_dist(x, y):
        if not obs_set:
            return 6
        md = 10**9
        for bx, by in obs_set:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best = [0, 0]
    best_val = None

    # Deterministic tie-break: fixed move order, so only replace on strictly better.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        d_opp = manhattan(nx, ny, ox, oy)
        do = nearest_obst_dist(nx, ny)

        if is_pursuer:
            # Chase tightly, avoid getting too close to obstacles in case wall-running uses them as traps.
            # Also slightly prefer moves that reduce the distance most.
            target_corner_bonus = 0
            for cx, cy in corners:
                # Prefer steering opponent away from corners where pursuer might "lose line" around obstacles.
                # (Approximate by favoring states closer to center when opponent is near a corner.)
                if manhattan(ox, oy, cx, cy) <= manhattan(ox, oy, 0, 0) + manhattan(ox, oy, w - 1, h - 1):
                    target_corner_bonus = -0.05 * manhattan(nx, ny, cx, cy)
                    break
            val = (-10.0) * d_opp + (0.18 * do) + target_corner_bonus
        else:
            # Evader: maximize distance from pursuer, while staying clear of obstacles.
            far_corner = max(corners, key=lambda c: manhattan(c[0], c[1], ox, oy))
            val = (12.0) * d_opp + (0.22 * do) - (0.03 * manhattan(nx, ny, far_corner[0], far_corner[1]))

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]