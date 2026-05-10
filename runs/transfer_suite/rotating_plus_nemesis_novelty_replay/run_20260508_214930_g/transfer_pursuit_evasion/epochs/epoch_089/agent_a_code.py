def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda d: (d[0], d[1]))  # deterministic tiebreak

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)

        # obstacle avoidance: maximize min Manhattan distance to obstacles
        min_ob_d = 999
        if obs:
            for bx, by in obs:
                d = abs(nx - bx) + abs(ny - by)
                if d < min_ob_d:
                    min_ob_d = d
        if not obs:
            min_ob_d = 4

        # corner bias (avoid being cornered by obstacles/walls when evading)
        corner_bias = -((nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1))

        # score components
        if is_pursuer:
            # minimize distance; strongly prefer non-increasing pursuit
            val = (-dist * 10) + (min_ob_d * 1.5) + corner_bias
        else:
            # maximize distance while keeping away from obstacles
            val = (dist * 10) + (min_ob_d * 1.5) + corner_bias

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]