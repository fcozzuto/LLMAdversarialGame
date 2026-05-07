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

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent; if impossible, minimize opponent lead.
        lead = od - sd
        reachable_adv = 1 if sd <= od else 0
        # Deterministic tie-break: closer to center if still tied.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(tx - cx) + abs(ty - cy)
        key = (reachable_adv, lead, -sd, -center_pen, -(tx + 31 * ty), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dist = man(nx, ny, tx, ty)
            # Prefer shorter distance; deterministic tie: dx then dy ordering.
            moves.append((dist, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [moves[0][1], moves[0][2]]