def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        elif isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    targets.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if targets:
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    op = observation.get("opponent_position") or [sx, sy]
    ox, oy = int(op[0]), int(op[1])
    best = None
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = abs(ox - nx) + abs(oy - ny)
        if d < bestd or (d == bestd and (dx, dy) < best):
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]