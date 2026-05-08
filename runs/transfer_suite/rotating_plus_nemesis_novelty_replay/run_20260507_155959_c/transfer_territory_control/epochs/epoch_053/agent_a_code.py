def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    candidates = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for c in unclaimed:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        if 0 <= ox < w and 0 <= oy < h and (ox, oy) not in obs:
            targets = [(ox, oy)]
        else:
            targets = [(sx, sy)]

    best = None
    for dx, dy, nx, ny in candidates:
        # Deterministic: closest unclaimed; tie-break toward opponent.
        bestd = None
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if bestd is None or d < bestd:
                bestd = d
        oppd = abs(ox - nx) + abs(oy - ny)
        key = (bestd, oppd, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]