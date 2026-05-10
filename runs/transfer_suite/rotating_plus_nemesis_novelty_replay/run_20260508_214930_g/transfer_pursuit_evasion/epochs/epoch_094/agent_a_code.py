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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = None
    best_corner = -1
    for cx, cy in corners:
        d = abs(cx - ox) + abs(cy - oy)
        if d > best_corner:
            best_corner = d
            far_corner = (cx, cy)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort(key=lambda t: (t[0], t[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_proximity(x, y):
        if not obs:
            return 0
        m = 10
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < m:
                m = d
        return m

    best_move = (0, 0)
    if is_pursuer:
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                val = None
            else:
                dist = abs(nx - ox) + abs(ny - oy)
                prox = obs_proximity(nx, ny)  # smaller is worse
                capture = 1 if (nx == ox and ny == oy) else 0
                val = (-capture * 1000) + dist * 1.0 + (1.0 / (prox + 1.0)) * 0.7
            if val is None:
                continue
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        tx, ty = far_corner
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                val = None
            else:
                dist_to_op = abs(nx - ox) + abs(ny - oy)
                prox = obs_proximity(nx, ny)  # larger is safer
                toward_corner = abs(tx - ox) + abs(ty - oy) - (abs(tx - nx) + abs(ty - ny))
                # score: primarily maximize distance from pursuer, then keep safe, then bias toward far corner from pursuer
                val = -dist_to_op * 1.0 - (prox * 0.35) - (toward_corner * 0.08)
            if val is None:
                continue
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]