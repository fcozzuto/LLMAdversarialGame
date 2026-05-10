def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = "purs" in self_role or "hunter" in self_role or self_role == "pursuer"
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def nearest_obs_d2(x, y):
        best = 10**9
        for (px, py) in obs:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best if obs else 10**6

    best_move = [0, 0]
    best_cost = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            cost = 10**12
        else:
            d = dist2(nx, ny, ox, oy)
            nd = nearest_obs_d2(nx, ny)
            if pursuer:
                # Minimize distance to opponent; prefer staying away from obstacles to avoid getting stuck.
                cost = d * 10 - nd
            else:
                # Maximize distance from opponent; prefer positions away from obstacles.
                cost = -d * 10 - nd
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = [dx, dy]

    return best_move