def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set()
    for c in unclaimed:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed_set.add((x, y))

    opp_terr = observation.get("opponent_territory") or []
    opp_set = set()
    for c in opp_terr:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                opp_set.add((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    candidates = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        val = 0.0
        if (nx, ny) in unclaimed_set:
            val += 3.5
        if (nx, ny) in opp_set:
            val += 6.0

        # Prefer reducing distance to center (territory control tends to spread)
        val += 0.12 * (dist(sx, sy, cx, cy) - dist(nx, ny, cx, cy))

        # If adjacent to opponent, prioritize capturing their territory or cutting them off
        manh_before = abs(sx - ox) + abs(sy - oy)
        manh_after = abs(nx - ox) + abs(ny - oy)
        if manh_after <= 2:
            val += 2.0 * (manh_before - manh_after)
            if (nx, ny) in opp_set:
                val += 2.0

        # Mild tie-break toward deterministic "right, down, stay" ordering
        tie = (dx, dy)
        val += 0.0001 * (tie[0] + 2 * tie[1])

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]