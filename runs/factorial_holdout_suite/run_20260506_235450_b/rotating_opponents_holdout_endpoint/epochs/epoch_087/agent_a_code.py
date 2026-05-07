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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None  # (key, tx, ty)
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent; then closer; then consistent tie-break by position.
        key = (od - sd, -min(sd, od), -(tx + ty), tx, ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)

    if best is None:
        # No valid resource: just move toward center while avoiding obstacles.
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    # Deterministically choose the move that decreases our distance to target most; penalize obstacles.
    best_m = (None, None)  # (score, move)
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            score = (-10**9,)
        else:
            before = man(sx, sy, tx, ty)
            after = man(nx, ny, tx, ty)
            score = (before - after, -after, (nx + ny))
        if best_m[0] is None or score > best_m[0]:
            best_m = (score, (mx, my))

    return [int(best_m[1][0]), int(best_m[1][1])]