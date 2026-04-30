def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not inside(sx, sy):
        sx, sy = 0, 0
        if not inside(sx, sy):
            for dx, dy in moves:
                if inside(sx + dx, sy + dy):
                    return [dx, dy]
            return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_self = min(man(nx, ny, rx, ry) for rx, ry in res)
            d_op = man(nx, ny, ox, oy)
            score = -d_self + 0.15 * d_op
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best is not None else [0, 0]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            score = -man(nx, ny, tx, ty) + 0.05 * man(nx, ny, ox, oy)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best is not None else [0, 0]