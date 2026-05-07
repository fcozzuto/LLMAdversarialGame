def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    # obstacle clutter penalty around cell (encourages smoother paths / less denial)
    def clutter(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Select target that maximizes being ahead while still progress-friendly and not too cluttered
    best_t = None
    best_s = None
    for tx, ty in res:
        my_d = manh(sx, sy, tx, ty)
        opp_d = manh(ox, oy, tx, ty)
        adv = opp_d - my_d  # positive => we are closer
        # Prefer: being closer than opponent; then shorter path; then less clutter
        s = adv * 1000 - my_d * 10 - clutter(tx, ty)
        if best_s is None or s > best_s:
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = None
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d2 = manh(nx, ny, tx, ty)
        opp_d2 = manh(ox, oy, tx, ty)
        adv2 = opp_d2 - my_d2
        # Want to decrease our distance; keep advantage; avoid stepping into clutter
        ms = adv2 * 1000 - my_d2 * 10 - clutter(nx, ny) - (1 if (dx == 0 and dy == 0) else 0)
        # Deterministic tie-break: prefer diagonal then straight then stay, with consistent ordering
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move