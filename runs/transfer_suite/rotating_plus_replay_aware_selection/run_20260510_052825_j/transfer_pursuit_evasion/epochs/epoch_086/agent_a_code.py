def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role) or (not evader)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = list(blocked)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def nearest_obs_d2(x, y):
        if not obstacles:
            return 10**9
        md = 10**9
        for ox2, oy2 in obstacles:
            dd = dist2(x, y, ox2, oy2)
            if dd < md:
                md = dd
        return md

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        d2o = dist2(nx, ny, ox, oy)
        obs_d2 = nearest_obs_d2(nx, ny)

        # obstacle avoidance: strong when near obstacles
        obs_term = 0
        if obstacles:
            obs_term = 1.0 / (1.0 + obs_d2)

        # pursuer wants closer to opponent; evader wants farther
        if pursuer:
            val = -d2o - 2.5 * obs_term
        else:
            val = d2o + 2.5 * (1.0 - obs_term)

        # deterministic tie-break: prefer smaller dx, then dy
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]