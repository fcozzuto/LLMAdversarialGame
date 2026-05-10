def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    cx, cy = w // 2, h // 2
    target = (cx, cy)
    if res:
        target = min(res, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d_t = abs(nx - target[0]) + abs(ny - target[1])
        d_o = abs(nx - ox) + abs(ny - oy)

        # Prefer moving toward target, and away from opponent; slight preference for survival (staying in bounds)
        key = (-(d_t), d_o, -abs(nx - cx) - abs(ny - cy), -abs(dx) - abs(dy))
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]