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
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer")
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def nearest_obs_d2(x, y):
        if not obs:
            return 10**9
        best = 10**9
        for px, py in obs:
            d = dist2(x, y, px, py)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    # For evasion, head to far corner; for pursuit, reduce distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    # Deterministic tie-break ordering: prefer smaller index in dirs.
    best_i = 4
    best_val = None

    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_op = dist2(nx, ny, ox, oy)
        d_obs = nearest_obs_d2(nx, ny)

        if pursuer:
            # minimize distance to opponent, keep away from obstacles
            val = (-d_op, d_obs)
        else:
            # maximize distance to opponent; also prefer moving toward far_corner
            target = dist2(nx, ny, far_corner[0], far_corner[1])
            val = (d_op, -target, d_obs)

        if best_val is None or val > best_val:
            best_val = val
            best_i = i

    dx, dy = dirs[best_i]
    return [int(dx), int(dy)]