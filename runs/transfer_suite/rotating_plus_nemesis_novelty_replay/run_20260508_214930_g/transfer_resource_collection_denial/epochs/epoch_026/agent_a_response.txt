def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resset.append((x, y))

    if not resset:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = None
    for rx, ry in resset:
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        margin = oppd - myd  # positive => we reach first
        center = abs(rx - cx) + abs(ry - cy)
        # Prefer safely attainable targets early, and avoid moves that are too slow overall.
        # Deterministic tie-break uses coordinates.
        safe_bonus = 0
        if margin > 0:
            safe_bonus = 1000 + 10 * margin
        elif margin == 0:
            safe_bonus = 200
        time_pen = 0
        if turns_remaining > 0:
            # discourage targets unlikely to be reached in time; keep deterministic
            if myd > turns_remaining:
                time_pen = (myd - turns_remaining) * 50
        key_score = (safe_bonus + margin * 10 - myd - center - time_pen, -myd, -center, -(rx * 100 + ry))
        if best_score is None or key_score > best_score:
            best_score = key_score
            best = (rx, ry)

    tx, ty = best

    # Move one step toward target (diagonal allowed). If blocked by obstacle, try axis-aligned alternatives.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for ndx, ndy in candidates:
        nx, ny = sx + ndx, sy + ndy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [int(ndx), int(ndy)]

    return [0, 0]