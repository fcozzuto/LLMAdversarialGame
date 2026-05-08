def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)
    i_am_pursuer = ("pursuer" in self_role) or ("evader" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx + dy

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    relx, rely = ox - sx, oy - sy
    step_toward = (sign(relx), sign(rely))
    step_away = (-step_toward[0], -step_toward[1])

    # Deterministic tie-breaker order preference: prefer staying unblocked and moving "useful"
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = manh(nx, ny)

        # Zigzag-friendly: if evading, don't just maximize distance; also prefer lateral moves that reduce pursuer alignment.
        # If pursuing, prefer moves that decrease distance and keep pressure directionally.
        if i_am_evader:
            # distance score primary
            val = d * 100.0
            # lateral bonus relative to current line to pursuer
            lat = abs((nx - sx) * step_away[1] - (ny - sy) * step_away[0])
            val += lat * 3.0
            # avoid moving directly toward pursuer when possible
            toward = 1.0 if (dx, dy) == step_toward else 0.0
            val -= toward * 8.0
        else:
            # pursuer strategy
            val = -d * 100.0
            # keep moving toward pursuer direction
            toward = 1.0 if (dx, dy) == step_toward else 0.0
            val += toward * 8.0
            # discourage stepping into obstacles-adjacent squares if possible
            adj_pen = 0.0
            for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                    adj_pen += 1.0
            val -= adj_pen * 1.5

        # deterministic tie-break: lexical order on (dx,dy) when values equal-ish
        if best is None or val > best_val + 1e-9 or (abs(val - best_val) <= 1e-9 and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]