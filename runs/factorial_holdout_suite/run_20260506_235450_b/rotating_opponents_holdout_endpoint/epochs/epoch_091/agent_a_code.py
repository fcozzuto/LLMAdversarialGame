def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_tx, best_ty = sx, sy
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Opponent sweeps rows: contest more when on same row as opponent.
        contest = 1 if ty == oy else 0
        key = (sd - od + contest * 3, sd + contest * 2, tx, ty)  # lower is better
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    dx_raw = 0 if best_tx == sx else (1 if best_tx > sx else -1)
    dy_raw = 0 if best_ty == sy else (1 if best_ty > sy else -1)
    candidates = [(dx_raw, dy_raw), (dx_raw, 0), (0, dy_raw), (0, 0)]
    best_move = [0, 0]
    best_local = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = man(nx, ny, best_tx, best_ty)
        # Mild anti-stuck: prefer moves that also reduce distance to opponent-row resources.
        local_key = (dist, abs((ny - oy)) + abs((nx - ox)), dx, dy)
        if best_local is None or local_key < best_local:
            best_local = local_key
            best_move = [dx, dy]
    return best_move