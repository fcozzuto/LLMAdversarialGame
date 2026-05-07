def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
            best = (d, (x, y))
    tx, ty = best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # deterministic fallback: try cardinal then stay
        cands = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
        for adx, ady in cands:
            nx2, ny2 = sx + adx, sy + ady
            if -1 <= adx <= 1 and -1 <= ady <= 1 and 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [int(adx), int(ady)]
        return [0, 0]
    return [int(dx), int(dy)]