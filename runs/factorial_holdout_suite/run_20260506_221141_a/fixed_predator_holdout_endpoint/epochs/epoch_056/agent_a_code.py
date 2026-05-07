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
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def kd(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Prefer resources we can race first (larger opp-self distance margin); tie-break by smaller our distance.
    best = None
    best_key = None
    for t in resources:
        sd = kd((sx, sy), t)
        od = kd((ox, oy), t)
        key = (od - sd, -sd, t[0], t[1])
        if best is None or key > best_key:
            best, best_key = t, key

    tx, ty = best

    # Choose among legal one-step moves the move that most reduces our distance to target,
    # with obstacle-avoidance and deterministic tie-breaking.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sd2 = kd((nx, ny), (tx, ty))
        # secondary: keep also from getting closer to opponent's distance to the same target (deny on approach)
        od2 = kd((ox, oy), (tx, ty))
        val = (-sd2, sd2 - od2, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move