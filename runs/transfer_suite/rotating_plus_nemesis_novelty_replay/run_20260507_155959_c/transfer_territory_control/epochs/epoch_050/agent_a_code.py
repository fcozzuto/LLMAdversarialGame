def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for c in unclaimed:
        if c is not None and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))

    if targets:
        tx, ty = targets[0]
        bestd = abs(tx - sx) + abs(ty - sy)
        for x, y in targets[1:]:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd, tx, ty = d, x, y
    else:
        tx, ty = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        adv = 0
        if (nx, ny) == (tx, ty):
            adv = -1000
        # Deterministic tie-break: prefer smaller dx, then dy
        score = dist + adv + (dx * 100 + dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]